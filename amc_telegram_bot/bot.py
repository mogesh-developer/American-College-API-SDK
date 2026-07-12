import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telebot import TeleBot
from .config import TELEGRAM_BOT_TOKEN
from .database.sqlite import init_db
from .handlers import start, profile, attendance, timetable, fees, notifications, news, settings

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
        
    def log_message(self, format, *args):
        # Suppress request logging to keep Render console logs clean
        return

def start_dummy_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Render health check server listening on port {port}...")
    server.serve_forever()

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
        sys.exit(1)

    # Start dummy web server on a background thread for Render port binding
    threading.Thread(target=start_dummy_web_server, daemon=True).start()

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
