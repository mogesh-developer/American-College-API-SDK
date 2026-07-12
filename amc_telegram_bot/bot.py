import sys
from telebot import TeleBot
from .config import TELEGRAM_BOT_TOKEN
from .database.sqlite import init_db
from .handlers import start, profile, attendance, timetable, fees, notifications, news, settings


def main():

    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
        sys.exit(1)

    print("Initializing database...")
    init_db()

    print("Starting background scheduler...")
    from .utils.scheduler import start_scheduler
    start_scheduler()

    print("Initializing Telegram bot...")
    bot = TeleBot(TELEGRAM_BOT_TOKEN)

    start.register_handlers(bot)
    profile.register_handlers(bot)
    attendance.register_handlers(bot)
    timetable.register_handlers(bot)
    fees.register_handlers(bot)
    notifications.register_handlers(bot)
    news.register_handlers(bot)
    settings.register_handlers(bot)

    print("Bot is polling... Press Ctrl+C to stop.")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("Bot stopped.")


if __name__ == "__main__":
    main()
