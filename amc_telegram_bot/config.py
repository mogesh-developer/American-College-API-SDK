import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "1424996266")

