from telebot import TeleBot
from telebot.types import Message
from ..utils.sdk_helper import get_client_for_user, UserNotRegistered
from amc_api.exceptions import LoginError
from ..database.sqlite import get_cached_profile, save_profile
import threading

# Helper to format student profile report card
def format_profile_message(p):

    return (
        "🎓 *STUDENT PROFILE REPORT*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 *Name:* `{p['student_name']}`\n"
        f"🆔 *Register No:* `{p['register_no']}`\n"
        f"🏫 *Department:* `{p['department_name']}`\n"
        f"📚 *Semester:* `Semester {p['semester']}`\n"
        f"📧 *Email:* `{p['email']}`\n"
        f"📞 *Mobile:* `{p['mobile']}`\n"
        f"📅 *Batch:* `{p['batch']}`\n"
        f"🗓️ *Academic Year:* `{p['college_year']}`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def fetch_profile_background(bot: TeleBot, chat_id: int, message_id: int, cached_p: dict):

    try:
        client = get_client_for_user(chat_id)
        profile = client.profile()
        if not profile:
            raise ValueError("Profile data is empty")

        save_profile(chat_id, profile)

        fresh_p = {
            "student_name": profile.student_name,
            "register_no": profile.register_no,
            "email": profile.email,
            "mobile": profile.mobile,
            "semester": profile.semester,
            "course_name": profile.course_name,
            "department_name": profile.department_name,
            "batch": profile.batch,
            "college_year": profile.college_year
        }

        final_text = format_profile_message(fresh_p)
        if cached_p and all(cached_p[k] == fresh_p[k] for k in fresh_p):
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
        if cached_p:
            final_text = format_profile_message(cached_p)
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

    @bot.message_handler(func=lambda msg: msg.text in ("🎓 Profile", "👤 Profile", "/profile"))
    def cmd_profile(message: Message):

        # Instantly display cached profile from SQLite
        cached_p = get_cached_profile(message.chat.id)

        if cached_p:
            initial_text = format_profile_message(cached_p)
            initial_text += "\n\n🔄 _Checking for updates..._"
        else:
            initial_text = "🔄 *Fetching student profile from portal...*"

        msg = bot.send_message(message.chat.id, initial_text, parse_mode="Markdown")

        # Spawn asynchronous thread to update database and edit message non-blockingly
        threading.Thread(
            target=fetch_profile_background,
            args=(bot, message.chat.id, msg.message_id, cached_p),
            daemon=True
        ).start()
