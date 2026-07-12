from telebot import TeleBot
from telebot.types import Message
from ..utils.sdk_helper import get_client_for_user


def register_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda msg: msg.text in ("🔔 Notifications", "/notifications"))
    def cmd_notifications(message: Message):

        client = get_client_for_user(message.chat.id)

        if not client:
            bot.send_message(message.chat.id, "Please log in first using `/login`.")
            return

        loading_msg = bot.send_message(message.chat.id, "Checking notifications...")

        try:
            notif = client.notification_count()
            text = (
                "🔔 *Notifications*\n\n"
                f"You have *{notif.count}* unread notifications."
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
                text=f"Failed to fetch notifications: {str(e)}"
            )
