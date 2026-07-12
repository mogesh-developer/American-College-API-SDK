from telebot import TeleBot
from telebot.types import Message
from ..utils.sdk_helper import get_client_for_user


def register_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda msg: msg.text in ("📰 News", "/news"))
    def cmd_news(message: Message):

        client = get_client_for_user(message.chat.id)

        if not client:
            bot.send_message(message.chat.id, "Please log in first using `/login`.")
            return

        loading_msg = bot.send_message(message.chat.id, "Fetching news & announcements...")

        try:
            news_items = client.news()
            text = "📰 *Latest News & Announcements*\n\n"

            if news_items:
                for idx, item in enumerate(news_items[:5], 1):
                    text += f"{idx}. *{item.title}* ({item.published_date})\n{item.content}\n\n"
            else:
                text += "_No announcements found._"

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
                text=f"Failed to fetch news: {str(e)}"
            )
