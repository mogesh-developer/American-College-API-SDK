import os
import re
import time
import logging
import pytz
import urllib.request
from datetime import datetime, timedelta
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot
from ..config import TELEGRAM_BOT_TOKEN, ADMIN_TELEGRAM_ID
from ..database.supabase_db import (
    get_all_users,
    get_weekly_timetable,
    save_profile
)
from .sdk_helper import get_client_for_user, UserNotRegistered

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Timetable hour to time-slot mapping
HOUR_TIMING_MAP = {
    1: "9:00 - 10:00",
    2: "10:00 - 11:00",
    3: "11:00 - 12:00",
    4: "12:00 - 1:00",
    5: "1:00 - 2:00",
    6: "2:00 - 3:00"
}

PERIOD_NUMBERS = {
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣"
}

PERIOD_CLOCK_EMOJIS = {
    1: "🕘",
    2: "🕙",
    3: "🕚",
    4: "🕛",
    5: "🕐",
    6: "🕑"
}

SUBJECT_ABBREVIATIONS = {
    "Natural Language Processing": "NLP",
    "Advanced Software Engineering": "ASE",
    "Advanced Database Management System": "ADBMS",
    "Data Mining & Warehousing": "DMW",
    "Digital Image Processing": "DIP",
    "Advanced Database Management System Lab": "ADBMS Lab",
    "Digital Image Processing Lab": "DIP Lab"
}


def send_morning_notification_to_user(telegram_id, date_display):
    try:
        client = get_client_for_user(telegram_id)
        profile = client.profile()
        
        # Cache updated profile in database
        try:
            save_profile(telegram_id, profile)
        except Exception as p_err:
            logger.error(f"Failed to cache profile for {telegram_id}: {p_err}")

        # Fetch day order status directly from college portal
        day_val_str = "Holiday"
        try:
            day_val_obj = client.timetable_day_value()
            if day_val_obj:
                if day_val_obj.is_holiday:
                    day_val_str = "Holiday"
                elif day_val_obj.day_order_text:
                    day_val_str = f"Day Order {day_val_obj.day_order_text}"
        except Exception as e:
            logger.error(f"Error fetching day value for {telegram_id}: {e}")

        # Map e.g. "Day Order 3" or "3" to "D3"
        day_key = None
        if day_val_str.startswith("Day Order "):
            num = day_val_str.split(" ")[-1]
            day_key = f"D{num}"
        elif day_val_str.isdigit():
            day_key = f"D{day_val_str}"

        message_lines = [
            "📅 *Today's Timetable*",
            "",
            f"🗓 *Date :* `{date_display}`",
            f"📖 *Day Order :* `{day_key or day_val_str}`",
            "",
            "━━━━━━━━━━━━━━",
            ""
        ]

        # Check portal timetable first for student-specific dynamic schedule
        has_classes = False
        try:
            tt = client.timetable(type_str="today")
            if tt and not tt.is_holiday and tt.schedule:
                has_classes = True
                for item in tt.schedule:
                    hour = item.hour
                    name = item.subject_name or (f"Subject #{item.subject_id}" if item.subject_id else "Class")
                    abbr = SUBJECT_ABBREVIATIONS.get(name, name)
                    clock_emoji = PERIOD_CLOCK_EMOJIS.get(hour, "🕒")
                    message_lines.append(f"{clock_emoji} H{hour} • {abbr}")
                    message_lines.append("")
        except Exception as tt_err:
            logger.debug(f"Direct portal timetable fetch skipped: {tt_err}")

        # Fallback to day order weekly schedule table if portal schedule is empty
        if not has_classes and day_key:
            try:
                schedule = get_weekly_timetable(day_key)
                if schedule:
                    has_classes = True
                    for entry in schedule:
                        hour = entry.get("hour")
                        name = entry.get("name")
                        abbr = SUBJECT_ABBREVIATIONS.get(name, name)
                        clock_emoji = PERIOD_CLOCK_EMOJIS.get(hour, "🕒")
                        
                        message_lines.append(f"{clock_emoji} H{hour} • {abbr}")
                        message_lines.append("")
            except Exception as schedule_err:
                logger.error(f"Error retrieving schedule for {telegram_id}: {schedule_err}")


        if not has_classes:
            message_lines.append("🏖️ *Today is a Holiday / No Class Scheduled.* 🏖️")
            message_lines.append("")

        message_lines.append("━━━━━━━━━━━━━━")
        message_text = "\n".join(message_lines)

        # Send Telegram Message
        bot.send_message(chat_id=telegram_id, text=message_text, parse_mode="Markdown")
        logger.info(f"Morning schedule sent to user {telegram_id}")

    except UserNotRegistered:
        logger.warning(f"User {telegram_id} not registered. Skipping morning job.")
    except Exception as e:
        logger.error(f"Failed morning job for user {telegram_id}: {e}")


def morning_notification():
    """
    Morning job: Sends today's timetable to all users concurrently.
    """
    logger.info("Starting morning timetable notifications...")
    try:
        user_ids = get_all_users()
    except Exception as e:
        logger.error(f"Error fetching users for morning schedule: {e}")
        return

    date_display = datetime.now().strftime("%d %b %Y")

    with ThreadPoolExecutor(max_workers=10) as executor:
        for telegram_id in user_ids:
            executor.submit(send_morning_notification_to_user, telegram_id, date_display)


def send_attendance_notification_to_user(telegram_id, today_str, date_display, period_title="Afternoon"):
    try:
        client = get_client_for_user(telegram_id)
        
        # Fetch fresh full attendance containing all logs
        full_att = client.full_attendance()
        
        # Filter today's attendance records
        today_logs = [r for r in full_att.attendance_records if r.attendance_date == today_str]
        
        present_list = []
        absent_list = []
        for r in today_logs:
            sub_name = r.subject_name or (f"Subject #{r.subject_id}" if getattr(r, "subject_id", None) else "Class")
            clock_emoji = PERIOD_CLOCK_EMOJIS.get(r.hour_value, "🕒")
            entry_str = f"{clock_emoji} H{r.hour_value} • {sub_name}"
            
            leave_t = (r.leave_type or "").lower()
            if leave_t in ("p", "present"):
                present_list.append(entry_str)
            else:
                leave_remark = f" ({r.leave_remarks})" if getattr(r, "leave_remarks", None) else ""
                absent_list.append(f"{entry_str}{leave_remark}")

        icon = "☀️" if period_title == "Afternoon" else "🌙"
        message_lines = [
            f"{icon} *{period_title} Attendance Status Report*",
            "",
            f"🗓 *Date:* `{date_display}`",
            "━━━━━━━━━━━━━━━━━━━━━━━━━",
            ""
        ]

        if present_list:
            message_lines.append("✅ *Present Hours:*")
            for entry in present_list:
                message_lines.append(entry)
            message_lines.append("")

        if absent_list:
            message_lines.append("❌ *Absent / Leave Hours:*")
            for entry in absent_list:
                message_lines.append(entry)
            message_lines.append("")

        if not present_list and not absent_list:
            message_lines.append("ℹ️ *No attendance marked on the portal for today yet.*")
            message_lines.append("")

        message_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
        message_text = "\n".join(message_lines)

        bot.send_message(chat_id=telegram_id, text=message_text, parse_mode="Markdown")
        logger.info(f"{period_title} attendance update sent to user {telegram_id}")

    except UserNotRegistered:
        logger.warning(f"User {telegram_id} not registered. Skipping {period_title} job.")
    except Exception as e:
        logger.error(f"Failed {period_title} job for user {telegram_id}: {e}")


# In-memory store for last known bundle script and site health
_LAST_BUNDLE_HASH = None
_LAST_PORTAL_STATUS = 200


def check_portal_health_and_changes():
    """
    Ultra-lightweight piggyback check executed ONLY during scheduled runs:
    1. Fetches only the 1KB HTML root of the student portal.
    2. Checks HTTP response status (alerts if site down/maintenance).
    3. Detects if the college deployed a new JS bundle (new endpoints/features added).
    Uses minimal bandwidth (zero polling loop) to fit comfortably within Render free tier.
    """
    global _LAST_BUNDLE_HASH, _LAST_PORTAL_STATUS
    try:
        url = "https://portal.americancollege.edu.in/mob/"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            code = resp.getcode()
            html = resp.read().decode("utf-8", errors="ignore")
            
            # Check for script bundle hash changes
            match = re.search(r'src="(/mob/assets/[^"]+\.js)"', html)
            current_bundle = match.group(1) if match else None

            if _LAST_BUNDLE_HASH is None:
                _LAST_BUNDLE_HASH = current_bundle
            elif current_bundle and current_bundle != _LAST_BUNDLE_HASH:
                _LAST_BUNDLE_HASH = current_bundle
                if ADMIN_TELEGRAM_ID:
                    bot.send_message(
                        chat_id=int(ADMIN_TELEGRAM_ID),
                        text=(
                            "🚀 *College Portal Update Detected!*\n\n"
                            f"The student portal has deployed a new web client bundle:\n`{current_bundle}`\n\n"
                            "New endpoints, features, or UI changes may be available."
                        ),
                        parse_mode="Markdown"
                    )

            if _LAST_PORTAL_STATUS != 200 and code == 200:
                _LAST_PORTAL_STATUS = 200
                if ADMIN_TELEGRAM_ID:
                    bot.send_message(
                        chat_id=int(ADMIN_TELEGRAM_ID),
                        text="✅ *Portal Restored:* The American College student portal is back online."
                    )

    except Exception as e:
        if _LAST_PORTAL_STATUS == 200:
            _LAST_PORTAL_STATUS = 500
            if ADMIN_TELEGRAM_ID:
                try:
                    bot.send_message(
                        chat_id=int(ADMIN_TELEGRAM_ID),
                        text=f"⚠️ *Portal Outage Alert:*\nUnable to reach student portal during scheduled run:\n`{str(e)}`"
                    )
                except Exception:
                    pass


def dispatch_attendance_notification(period_title):
    """
    Sends today's live attendance updates to all users concurrently.
    Also piggybacks a lightweight site health and bundle check.
    """
    logger.info(f"Starting {period_title} attendance notifications...")

    # Passive check during the attendance run (no extra continuous loop)
    check_portal_health_and_changes()

    try:
        user_ids = get_all_users()
    except Exception as e:
        logger.error(f"Error fetching users for {period_title} attendance schedule: {e}")
        return


    today_str = datetime.now().strftime("%Y-%m-%d")
    date_display = datetime.now().strftime("%d %b %Y")

    with ThreadPoolExecutor(max_workers=10) as executor:
        for telegram_id in user_ids:
            executor.submit(send_attendance_notification_to_user, telegram_id, today_str, date_display, period_title)


def afternoon_attendance_notification():
    """2:00 PM Attendance check"""
    dispatch_attendance_notification("Afternoon (2:00 PM)")


def send_weekly_recap_to_user(telegram_id):
    try:
        client = get_client_for_user(telegram_id)
        full_att = client.full_attendance()
        
        # Calculate start of current week (Monday) to today (Friday)
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        week_start_str = start_of_week.strftime("%Y-%m-%d")
        week_end_str = today.strftime("%Y-%m-%d")

        week_logs = [
            r for r in full_att.attendance_records
            if week_start_str <= r.attendance_date <= week_end_str
        ]

        if not week_logs:
            return

        present_hours = sum(1 for r in week_logs if (r.leave_type or "").lower() in ("p", "present"))
        absent_hours = len(week_logs) - present_hours
        week_pct = round((present_hours / len(week_logs)) * 100, 1) if week_logs else 0.0

        message_lines = [
            "📊 *WEEKLY ATTENDANCE RECAP (Mon - Fri)*",
            "━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"🗓 *Period:* `{week_start_str}` to `{week_end_str}`",
            "",
            f"✅ *Classes Attended:* `{present_hours}` hours",
            f"❌ *Classes Missed:* `{absent_hours}` hours",
            f"🎯 *Weekly Attendance:* `{week_pct}%`",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━",
            "💡 _Use /bunk anytime to check your margin before taking leave._"
        ]

        bot.send_message(chat_id=telegram_id, text="\n".join(message_lines), parse_mode="Markdown")
        logger.info(f"Weekly recap sent to user {telegram_id}")

    except Exception as e:
        logger.error(f"Error sending weekly recap to {telegram_id}: {e}")


def weekly_recap_notification():
    """Friday 5:00 PM Weekly Recap"""
    logger.info("Starting Friday weekly attendance recap notifications...")
    try:
        user_ids = get_all_users()
    except Exception as e:
        logger.error(f"Error fetching users for weekly recap: {e}")
        return

    with ThreadPoolExecutor(max_workers=10) as executor:
        for telegram_id in user_ids:
            executor.submit(send_weekly_recap_to_user, telegram_id)


def evening_attendance_notification():
    """7:00 PM Attendance check"""
    dispatch_attendance_notification("Evening (7:00 PM)")



# Global Scheduler Instance with India Standard Time (IST)
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Kolkata"))


def start_scheduler():
    """
    Start the background scheduler with cron jobs.
    1. Morning (8:45 AM IST): Day Order & Today's classes
    2. Afternoon (2:00 PM IST): Attendance status check (Present/Absent)
    3. Evening (7:00 PM IST): Final daily attendance status check (Present/Absent)
    """
    if not scheduler.running:
        # Schedule morning notification at 8:45 AM IST
        scheduler.add_job(
            morning_notification,
            "cron",
            hour=8,
            minute=45,
            id="morning_job",
            replace_existing=True
        )
        
        # Schedule afternoon notification at 2:00 PM IST (14:00)
        scheduler.add_job(
            afternoon_attendance_notification,
            "cron",
            hour=14,
            minute=0,
            id="afternoon_job_2pm",
            replace_existing=True
        )

        # Schedule Friday weekly attendance recap at 5:00 PM IST (17:00, day_of_week='fri')
        scheduler.add_job(
            weekly_recap_notification,
            "cron",
            day_of_week="fri",
            hour=17,
            minute=0,
            id="friday_weekly_recap_job",
            replace_existing=True
        )

        # Schedule evening notification at 7:00 PM IST (19:00)

        scheduler.add_job(
            evening_attendance_notification,
            "cron",
            hour=19,
            minute=0,
            id="evening_job_7pm",
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background scheduler started successfully with 8:45 AM, 2:00 PM, and 7:00 PM jobs in Asia/Kolkata timezone.")

