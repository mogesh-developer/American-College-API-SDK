from telebot import TeleBot
from telebot.types import Message
from ..utils.sdk_helper import get_client_for_user, UserNotRegistered
from amc_api.exceptions import LoginError
from ..database.sqlite import get_cached_attendance, save_attendance_logs
from collections import defaultdict
from datetime import datetime
import threading


class AbsentRecord:

    def __init__(self, date, hour, subject_id, subject_name=None):
        self.date = date
        self.hour = hour
        self.subject_id = subject_id
        self.subject_name = subject_name


SUBJECT_FALLBACK_MAP = {
    2501: "24PCS5409-NLP-VB (Natural Language Processing)",
    2500: "24PCS5407-ASE-CM (Advanced Software Engineering)",
    2497: "24PCS5403-ADBMS-KBA (Advanced DBMS)",
    2495: "24PCS5401-DMW-KS (Data Mining & Warehousing)",
    2499: "24PCS5405-DIP-KB (Digital Image Processing)",
    2494: "24PCS5301-ADBMS LAB-KBA (Advanced DBMS Lab)",
    2498: "24PCS5405-DIP LAB-KB (Digital Image Processing Lab)"
}


def make_progress_bar(percentage, length=12):

    filled = int(round(percentage / 100 * length))
    return "█" * filled + "░" * (length - filled)


def format_attendance_message(records, subject_map, reg_no=""):

    absent_hours = len(records)
    total_hours = 450
    percentage = max(0.0, min(100.0, ((total_hours - absent_hours) / total_hours) * 100))
    progress_bar = make_progress_bar(percentage)
    
    if percentage >= 75.0:
        status_str = "🟢 *SAFE* (>= 75%)"
    else:
        status_str = "🔴 *CRITICAL ATTENDANCE* (< 75%)"

    text = (
        "📊 *ATTENDANCE ANALYTICS DASHBOARD*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    if reg_no:
        text += f"👤 *Student:* `{reg_no}`\n"
        
    text += (
        f"🚨 *Total Absent:* `{absent_hours} Hours`\n"
        f"📈 *Estimated Rate:* `{percentage:.1f}%` \n"
        f"`[{progress_bar}]`\n\n"
        f"🚦 *Status:* {status_str}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )

    if not records:
        text += "🎉 *Flawless Attendance! No absences found.*\n━━━━━━━━━━━━━━━━━━━━━━━━━"
        return text

    text += "📅 *ABSENCE LOG HISTORY:*\n\n"

    grouped_absents = defaultdict(list)
    for r in records:
        grouped_absents[r.date].append(r)

    sorted_dates = sorted(grouped_absents.keys(), reverse=True)
    for raw_date in sorted_dates:
        day_items = sorted(grouped_absents[raw_date], key=lambda x: x.hour)

        try:
            parsed_dt = datetime.strptime(raw_date, "%Y-%m-%d")
            formatted_date = parsed_dt.strftime("%d-%m-%Y")
        except Exception:
            formatted_date = raw_date

        hours_str = ",".join(str(item.hour) for item in day_items)
        text += f"📅 *{formatted_date}* (Hours: {hours_str})\n"

        for idx, item in enumerate(day_items):
            sub_id = None
            try:
                sub_id = int(item.subject_id) if item.subject_id else None
            except ValueError:
                pass

            sub_name = item.subject_name or subject_map.get(sub_id) or SUBJECT_FALLBACK_MAP.get(sub_id)
            sub_display = f"*{sub_name}*" if sub_name else f"Subject ID: `{item.subject_id}`"
            
            connector = "└──" if idx == len(day_items) - 1 else "├──"
            text += f"  {connector} 🕒 *Hour {item.hour}:* {sub_display}\n"
        text += "\n"

    text += "━━━━━━━━━━━━━━━━━━━━━━━━━"
    return text


def fetch_attendance_background(bot: TeleBot, chat_id: int, message_id: int, cached_records: list):

    try:
        client = get_client_for_user(chat_id)
        fresh_absents = client.absent_days()

        subject_map = {}
        try:
            weekly_schedule = client.timetable(type_str="week")
            if weekly_schedule.schedule:
                for item in weekly_schedule.schedule:
                    if item.subject_id and item.subject_name:
                        try:
                            subject_map[int(item.subject_id)] = item.subject_name
                        except ValueError:
                            pass
        except Exception:
            pass

        save_attendance_logs(chat_id, fresh_absents, subject_map)

        fresh_records = [
            AbsentRecord(
                r.date,
                r.hour,
                r.subject_id,
                subject_map.get(int(r.subject_id) if r.subject_id else None)
            )
            for r in fresh_absents
        ]

        cached_sig = [(r.date, r.hour, r.subject_id) for r in cached_records]
        fresh_sig = [(r.date, r.hour, r.subject_id) for r in fresh_records]

        final_text = format_attendance_message(fresh_records, subject_map, reg_no=client.reg_no)

        if cached_sig == fresh_sig:
            final_text += "\n\n✅ _Synced (Up to date)_"
        else:
            final_text += "\n\n🆕 _Updated from portal_"

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=final_text,
            parse_mode="Markdown"
        )
    except Exception as e:
        if cached_records:
            final_text = format_attendance_message(cached_records, {}, reg_no="")
            final_text += f"\n\n⚠️ _Offline: Using cached data ({str(e)})_"
            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=final_text,
                    parse_mode="Markdown"
                )
            except Exception:
                pass


def register_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda msg: msg.text in ("📊 Attendance", "/attendance"))
    def cmd_attendance(message: Message):

        cached_rows = get_cached_attendance(message.chat.id)
        cached_records = [
            AbsentRecord(row["date"], row["hour"], row["subject_id"], row["subject_name"])
            for row in cached_rows
        ]

        # Render instant cached layout
        if cached_records:
            initial_text = format_attendance_message(cached_records, {}, reg_no="")
            initial_text += "\n\n🔄 _Checking for updates..._"
        else:
            initial_text = "🔄 *Fetching attendance details from portal...*"

        msg = bot.send_message(message.chat.id, initial_text, parse_mode="Markdown")

        # Spawn asynchronous thread to update database and edit message non-blockingly
        threading.Thread(
            target=fetch_attendance_background,
            args=(bot, message.chat.id, msg.message_id, cached_records),
            daemon=True
        ).start()
