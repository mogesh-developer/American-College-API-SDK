from telebot import TeleBot
from telebot.types import Message
from ..utils.sdk_helper import get_client_for_user


def register_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda msg: msg.text in ("🔄 Clear Cache", "/clear_cache", "/clearcache"))
    def cmd_clear_cache(message: Message):
        chat_id = message.chat.id
        from ..utils.session_manager import session_manager, attendance_cache
        from ..database.sqlite import supabase

        # 1. Clear memory session and attendance cache
        session_manager.remove_client(chat_id)
        if chat_id in attendance_cache:
            del attendance_cache[chat_id]

        # 2. Clear cached profile and attendance from Supabase
        try:
            supabase.table("student_profiles").delete().eq("telegram_id", chat_id).execute()
            supabase.table("attendance").delete().eq("telegram_id", chat_id).execute()
        except Exception:
            pass

        bot.send_message(
            chat_id,
            "🧹 *Cache Cleared Successfully!*\n\nAll cached profile, attendance, and session tokens have been refreshed from the server. Your next requests will fetch live data from the college portal.",
            parse_mode="Markdown"
        )

    @bot.message_handler(func=lambda msg: msg.text in ("⚙️ Settings", "/settings"))

    def cmd_settings(message: Message):

        client = get_client_for_user(message.chat.id)

        if not client:
            bot.send_message(message.chat.id, "Please log in first using `/login`.")
            return

        loading_msg = bot.send_message(message.chat.id, "Fetching settings...")

        try:
            settings = client.settings()
            text = (
                "⚙️ *Portal Settings*\n\n"
                f"*SMS Sender Name:* {settings.sms_sender_name}\n"
                f"*Staff Biometric Attendance:* {'Enabled' if settings.biometric_teaching_enable == '1' else 'Disabled'}\n"
                f"*Student Biometric Attendance:* {'Enabled' if settings.stud_biometric_enable == '1' else 'Disabled'}\n"
            )
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=loading_msg.message_id,
                text=text,
                parse_mode="Markdown"
            )
        except Exception as e:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=loading_msg.message_id,
                text=f"Failed to fetch settings: {str(e)}"
            )
