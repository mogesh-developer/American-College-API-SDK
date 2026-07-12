import os
import time
import logging
from datetime import datetime
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot
from ..config import TELEGRAM_BOT_TOKEN
from ..database.supabase_db import (
    get_all_users,
    get_cached_day_order,
    save_day_order,
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

def morning_notification():
    """
    Morning job runs at 8:00 AM: Sends today's timetable to all users.
    """
    logger.info("Starting morning timetable notifications...")
    try:
        user_ids = get_all_users()
    except Exception as e:
        logger.error(f"Error fetching users for morning schedule: {e}")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    date_display = datetime.now().strftime("%d-%m-%Y")

    for telegram_id in user_ids:
        try:
            client = get_client_for_user(telegram_id)
            profile = client.profile()
            
            # Cache updated profile in database
            try:
                save_profile(telegram_id, profile)
            except Exception as p_err:
                logger.error(f"Failed to cache profile for {telegram_id}: {p_err}")

            # Fetch day order status
            day_val_str = get_cached_day_order(today_str)
            if not day_val_str:
                try:
                    day_val_obj = client.timetable_day_value()
                    if day_val_obj:
                        if day_val_obj.is_holiday:
                            day_val_str = "Holiday"
                        else:
                            day_val_str = day_val_obj.day_order_text or "Holiday"
                        save_day_order(today_str, day_val_str)
                    else:
                        day_val_str = "Holiday"
                except Exception as e:
                    logger.error(f"Error fetching day value for {telegram_id}: {e}")
                    day_val_str = "Holiday"

            if not day_val_str:
                day_val_str = "Holiday"

            # Format Morning Message
            student_name = profile.student_name.split(" ")[0].capitalize() if profile.student_name else "Student"
            
            message_lines = [
                f"🌅 *Good Morning, {student_name}!*",
                "",
                f"📅 *Date:* `{date_display}`",
                f"📖 *Day Order:* `{day_val_str}`",
                ""
            ]

            # Map e.g. "Day Order 3" to "D3"
            has_classes = False
            if day_val_str.startswith("Day Order "):
                try:
                    num = day_val_str.split(" ")[-1]
                    day_key = f"D{num}"
                    schedule = get_weekly_timetable(day_key)
                    if schedule:
                        has_classes = True
                        message_lines.append("📚 *Today's Classes*")
                        message_lines.append("")
                        for entry in schedule:
                            hour = entry.get("hour")
                            code = entry.get("code")
                            name = entry.get("name")
                            staff = entry.get("staff")
                            
                            num_emoji = PERIOD_NUMBERS.get(hour, f"{hour}️⃣")
                            clock_emoji = PERIOD_CLOCK_EMOJIS.get(hour, "🕒")
                            timing = HOUR_TIMING_MAP.get(hour, "")
                            
                            message_lines.append(f"{num_emoji} *{name}*")
                            message_lines.append(f"👨‍🏫 {staff}")
                            if timing:
                                message_lines.append(f"{clock_emoji} {timing}")
                            message_lines.append("")
                except Exception as schedule_err:
                    logger.error(f"Error retrieving schedule for {telegram_id}: {schedule_err}")

            if not has_classes:
                message_lines.append("🏖️ *Today is a Holiday / No Class Scheduled.* 🏖️")
                message_lines.append("")

            message_lines.append("Have a great day! 🎓")
            message_text = "\n".join(message_lines)

            # Send Telegram Message
            bot.send_message(chat_id=telegram_id, text=message_text, parse_mode="Markdown")
            logger.info(f"Morning schedule sent to user {telegram_id}")

        except UserNotRegistered:
            logger.warning(f"User {telegram_id} not registered. Skipping morning job.")
        except Exception as e:
            logger.error(f"Failed morning job for user {telegram_id}: {e}")

def afternoon_notification():
    """
    Afternoon job runs at 2:00 PM: Sends today's attendance summary to all users.
    """
    logger.info("Starting afternoon attendance notifications...")
    try:
        user_ids = get_all_users()
    except Exception as e:
        logger.error(f"Error fetching users for afternoon schedule: {e}")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")

    for telegram_id in user_ids:
        try:
            client = get_client_for_user(telegram_id)
            
            # Fetch day order to check if today is a class day
            day_val_str = get_cached_day_order(today_str)
            if not day_val_str:
                try:
                    day_val_obj = client.timetable_day_value()
                    if day_val_obj:
                        if day_val_obj.is_holiday:
                            day_val_str = "Holiday"
                        else:
                            day_val_str = day_val_obj.day_order_text or "Holiday"
                    else:
                        day_val_str = "Holiday"
                except Exception:
                    day_val_str = "Holiday"

            
            # Only send if today is a school day (not a holiday/weekend)
            if not day_val_str or not day_val_str.startswith("Day Order "):
                logger.info(f"Skipping afternoon attendance for {telegram_id} because today is a Holiday/Weekend.")
                continue

            # Fetch fresh absent days
            fresh_absents = client.absent_days()
            
            # Filter and count today's absences
            today_absents = [r for r in fresh_absents if r.date == today_str]
            absent_hours_today = len(today_absents)
            present_hours_today = max(0, 5 - absent_hours_today) # Default 5 hour class day

            # Overall Attendance Percentage
            total_hours = 450
            absent_hours = len(fresh_absents)
            percentage = max(0.0, min(100.0, ((total_hours - absent_hours) / total_hours) * 100))

            # Format Message
            message_lines = [
                "🌇 *Attendance Summary*",
                "📊 *Today's Attendance*",
                "",
                f"✅ Present : {present_hours_today} Hours",
                "",
                f"❌ Absent : {absent_hours_today} Hour" if absent_hours_today == 1 else f"❌ Absent : {absent_hours_today} Hours",
                "",
                "Attendance Percentage:",
                f"*{percentage:.1f}%*",
                ""
            ]

            if percentage >= 75.0:
                message_lines.append("Keep it up! 🎉")
            else:
                message_lines.append("Warning: Attendance below 75%! ⚠️")

            message_text = "\n".join(message_lines)
            bot.send_message(chat_id=telegram_id, text=message_text, parse_mode="Markdown")
            logger.info(f"Afternoon attendance sent to user {telegram_id}")

        except UserNotRegistered:
            logger.warning(f"User {telegram_id} not registered. Skipping afternoon job.")
        except Exception as e:
            logger.error(f"Failed afternoon job for user {telegram_id}: {e}")

# Global Scheduler Instance
scheduler = BackgroundScheduler()

def start_scheduler():
    """
    Start the background scheduler with cron jobs.
    """
    if not scheduler.running:
        # Schedule morning notification (8:00 AM)
        scheduler.add_job(
            morning_notification,
            "cron",
            hour=8,
            minute=0,
            id="morning_job",
            replace_existing=True
        )
        
        # Schedule afternoon notification (2:00 PM / 14:00)
        scheduler.add_job(
            afternoon_notification,
            "cron",
            hour=14,
            minute=0,
            id="afternoon_job",
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background scheduler started successfully.")
