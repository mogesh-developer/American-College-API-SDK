from telebot import TeleBot
from telebot.types import Message
from ..utils.sdk_helper import get_client_for_user


def register_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda msg: msg.text in ("💰 Fees", "/fees"))
    def cmd_fees(message: Message):

        client = get_client_for_user(message.chat.id)

        if not client:
            bot.send_message(message.chat.id, "Please log in first using `/login`.")
            return

        loading_msg = bot.send_message(message.chat.id, "Fetching fees...")

        try:
            fees_data = client.fees(balance_only=True)
            text = (
                "💰 *Fees Status*\n\n"
                f"*Outstanding Balance:* ₹{fees_data.balance}\n\n"
            )

            groups = client.fee_service_groups()
            if groups.groups:
                text += "*Available Fee Service Groups:*\n"
                for group in groups.groups:
                    text += f"- {group.name}\n"
            else:
                text += "_No additional fee payment services available at this time._"

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
                text=f"Failed to fetch fees: {str(e)}"
            )
