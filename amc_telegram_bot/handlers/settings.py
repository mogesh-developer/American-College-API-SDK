from telebot import TeleBot
from telebot.types import Message
from ..utils.sdk_helper import get_client_for_user


def register_handlers(bot: TeleBot):

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
