from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ..utils.sdk_helper import get_client_for_user, UserNotRegistered
from amc_api.exceptions import LoginError
from ..database.sqlite import get_cached_attendance, save_attendance_logs
from collections import defaultdict
from datetime import datetime
import threading
import time
from ..keyboards.menu import main_menu


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


# Snappy in-memory cache
attendance_cache = {}


def make_progress_bar(percentage, length=10):
    filled = int(round(percentage / 100 * length))
    return "█" * filled + "░" * (length - filled)


def get_cached_student_name(chat_id):
    try:
        from ..database.supabase_db import get_cached_profile
        prof = get_cached_profile(chat_id)
        if prof and prof.get("student_name"):
            return prof["student_name"]
    except Exception:
        pass
    return "Student"


def get_base_attendance(chat_id, force_refresh=False):
    now = time.time()
    cached = attendance_cache.get(chat_id)
    if not force_refresh and cached and "subject_wise" in cached and (now - cached.get("last_updated", 0) < 600):
        return cached

    client = get_client_for_user(chat_id)
    subject_attendance_list = client.subject_wise_attendance()
    student_name = get_cached_student_name(chat_id)

    if not cached:
        cached = {}
    cached.update({
        "student_name": student_name,
        "reg_no": client.reg_no,
        "subject_wise": subject_attendance_list,
        "last_updated": now
    })
    attendance_cache[chat_id] = cached
    return cached


def get_absence_history_data(chat_id):
    cached = attendance_cache.get(chat_id)
    if cached and "absent_days" in cached:
        return cached

    client = get_client_for_user(chat_id)
    fresh_absents = client.absent_days()

    subject_map = {}
    if cached and "subject_wise" in cached:
        for sub in cached["subject_wise"]:
            subject_map[sub.subject_id] = sub.short_name or sub.subject_name

    records = [
        AbsentRecord(
            r.date,
            r.hour,
            r.subject_id,
            subject_map.get(int(r.subject_id) if r.subject_id else None)
        )
        for r in fresh_absents
    ]

    if not cached:
        cached = {}
    cached["absent_days"] = records
    attendance_cache[chat_id] = cached
    
    # Save to SQLite in background
    try:
        save_attendance_logs(chat_id, fresh_absents, subject_map)
    except Exception:
        pass

    return cached


def show_attendance_menu(bot: TeleBot, chat_id: int, message_id: int = None, force_refresh=False):
    try:
        if not message_id:
            msg = bot.send_message(chat_id, "🔄 *Loading attendance...*", parse_mode="Markdown")
            message_id = msg.message_id

        data = get_base_attendance(chat_id, force_refresh=force_refresh)

        # Calculate total absent hours & overall percentage from subject wise report
        absent_hours = int(sum(s.total_hours_absent for s in data["subject_wise"]))
        total_present = sum(s.total_hours_present for s in data["subject_wise"])
        total_hours = sum(s.total_hours for s in data["subject_wise"])
        percentage = (total_present / total_hours * 100) if total_hours > 0 else 100.0

        status_emoji = "🟢" if percentage >= 75.0 else "🔴"

        text = (
            "📊 *Attendance*\n\n"
            f"👤 *{data['student_name'].upper()}*\n\n"
            "📈 *Overall Attendance*\n"
            f"{status_emoji} `{percentage:.1f}%`\n\n"
            "❌ *Absent Hours*\n"
            f"`{absent_hours}`\n\n"
            "━━━━━━━━━━━━━━\n\n"
            "Select an option 👇"
        )

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("📅 Absence History", callback_data="att_history_0"),
            InlineKeyboardButton("📈 Subject Report", callback_data="att_subjects")
        )
        markup.add(
            InlineKeyboardButton("🔄 Refresh", callback_data="att_refresh"),
            InlineKeyboardButton("🏠 Home", callback_data="att_home")
        )

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        error_text = f"❌ *Error:* `{str(e)}`"
        if message_id:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=error_text, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, error_text, parse_mode="Markdown")


def show_absence_history(bot: TeleBot, chat_id: int, message_id: int, page=0):
    try:
        # Check if absent days cached, if not show loading
        cached = attendance_cache.get(chat_id)
        if not cached or "absent_days" not in cached:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🔄 *Loading absence logs...*", parse_mode="Markdown")
            get_absence_history_data(chat_id)

        data = attendance_cache.get(chat_id)
        grouped = defaultdict(list)
        for r in data["absent_days"]:
            grouped[r.date].append(r)

        sorted_dates = sorted(grouped.keys(), reverse=True)

        text = (
            "📅 *Absence History*\n\n"
            "Choose a date 👇"
        )

        markup = InlineKeyboardMarkup(row_width=1)

        start_idx = page * 5
        end_idx = start_idx + 5
        page_dates = sorted_dates[start_idx:end_idx]

        for d in page_dates:
            try:
                parsed_dt = datetime.strptime(d, "%Y-%m-%d")
                lbl = parsed_dt.strftime("📅 %d %b")
            except Exception:
                lbl = f"📅 {d}"
            markup.add(InlineKeyboardButton(lbl, callback_data=f"att_date_{d}"))

        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"att_history_{page-1}"))
        if end_idx < len(sorted_dates):
            nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"att_history_{page+1}"))
        if nav_row:
            markup.add(*nav_row)

        markup.add(
            InlineKeyboardButton("⬅️ Back", callback_data="att_menu"),
            InlineKeyboardButton("🏠 Home", callback_data="att_home")
        )

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ *Error:* `{str(e)}`",
            parse_mode="Markdown"
        )


def show_date_details(bot: TeleBot, chat_id: int, message_id: int, target_date: str):
    try:
        data = attendance_cache.get(chat_id)
        grouped = defaultdict(list)
        for r in data["absent_days"]:
            grouped[r.date].append(r)

        sorted_dates = sorted(grouped.keys(), reverse=True)
        if target_date not in grouped:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="⚠️ *No absence records found for this date.*",
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Back", callback_data="att_history_0")),
                parse_mode="Markdown"
            )
            return

        day_items = sorted(grouped[target_date], key=lambda x: x.hour)

        try:
            parsed_dt = datetime.strptime(target_date, "%Y-%m-%d")
            formatted_date = parsed_dt.strftime("%d %b %Y")
        except Exception:
            formatted_date = target_date

        text = f"📅 *{formatted_date}*\n\n"
        for item in day_items:
            sub_name = item.subject_name or SUBJECT_FALLBACK_MAP.get(int(item.subject_id) if item.subject_id else None) or f"Subject {item.subject_id}"
            text += f"⏰ *Hour {item.hour}*\n📖 `{sub_name}`\n\n"

        idx = sorted_dates.index(target_date)
        markup = InlineKeyboardMarkup(row_width=2)

        nav_buttons = []
        if idx + 1 < len(sorted_dates):
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"att_date_{sorted_dates[idx+1]}"))
        if idx - 1 >= 0:
            nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"att_date_{sorted_dates[idx-1]}"))

        if nav_buttons:
            markup.add(*nav_buttons)

        markup.add(
            InlineKeyboardButton("📅 Dates", callback_data="att_history_0"),
            InlineKeyboardButton("🏠 Home", callback_data="att_home")
        )

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ *Error:* `{str(e)}`",
            parse_mode="Markdown"
        )


def show_subject_report(bot: TeleBot, chat_id: int, message_id: int):
    try:
        data = attendance_cache.get(chat_id)

        text = (
            "📈 *Subject Attendance*\n\n"
            "Choose Subject"
        )

        markup = InlineKeyboardMarkup(row_width=2)
        for sub in data["subject_wise"]:
            name = sub.short_name or sub.subject_name
            if len(name) > 20:
                name = name[:18] + ".."
            markup.add(InlineKeyboardButton(f"📘 {name}", callback_data=f"att_subject_{sub.subject_id}"))

        markup.add(
            InlineKeyboardButton("⬅️ Back", callback_data="att_menu"),
            InlineKeyboardButton("🏠 Home", callback_data="att_home")
        )

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ *Error:* `{str(e)}`",
            parse_mode="Markdown"
        )


def show_subject_details(bot: TeleBot, chat_id: int, message_id: int, subject_id: int):
    try:
        data = attendance_cache.get(chat_id)

        sub = next((s for s in data["subject_wise"] if s.subject_id == subject_id), None)
        if not sub:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="⚠️ *Subject details not found.*",
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Back", callback_data="att_subjects")),
                parse_mode="Markdown"
            )
            return

        name = sub.short_name or sub.subject_name
        teacher = data.get("subject_teachers", {}).get(subject_id, "N/A")

        text = (
            f"📘 *{name}*\n\n"
            "Attendance\n"
            f"`{sub.total_percentage:.1f}%`\n\n"
            "Present\n"
            f"`{sub.total_hours_present}`\n\n"
            "Absent\n"
            f"`{int(sub.total_hours_absent)}`\n\n"
            "Faculty\n"
            f"*{teacher}*"
        )

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⬅️ Back", callback_data="att_subjects"),
            InlineKeyboardButton("🏠 Home", callback_data="att_home")
        )

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ *Error:* `{str(e)}`",
            parse_mode="Markdown"
        )


def register_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda msg: msg.text in ("📊 Attendance", "/attendance"))
    def cmd_attendance(message: Message):
        show_attendance_menu(bot, message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("att_"))
    def handle_attendance_callbacks(call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        data = call.data

        if data == "att_menu":
            show_attendance_menu(bot, chat_id, message_id)
        elif data == "att_refresh":
            show_attendance_menu(bot, chat_id, message_id, force_refresh=True)
        elif data.startswith("att_history_"):
            page = int(data.split("_")[-1])
            show_absence_history(bot, chat_id, message_id, page)
        elif data.startswith("att_date_"):
            target_date = data.split("att_date_")[-1]
            show_date_details(bot, chat_id, message_id, target_date)
        elif data == "att_subjects":
            show_subject_report(bot, chat_id, message_id)
        elif data.startswith("att_subject_"):
            sub_id = int(data.split("_")[-1])
            show_subject_details(bot, chat_id, message_id, sub_id)
        elif data == "att_home":
            try:
                bot.delete_message(chat_id, message_id)
            except Exception:
                pass
            bot.send_message(
                chat_id=chat_id,
                text="🏠 *Returned to Home Menu*",
                reply_markup=main_menu(),
                parse_mode="Markdown"
            )
