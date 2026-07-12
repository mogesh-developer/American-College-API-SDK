import os
import sys
import socket
from dotenv import load_dotenv

# Force IPv4 to prevent hanging on broken local IPv6/NAT64 networks
orig_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = patched_getaddrinfo

load_dotenv()

# Add current directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from amc_telegram_bot.utils.scheduler import morning_notification, afternoon_notification
from amc_telegram_bot.database.supabase_db import get_all_users

print("=== Running Manual Scheduler Jobs ===")
try:
    user_ids = get_all_users()
    print(f"Registered user IDs in Supabase: {user_ids}")
except Exception as e:
    print(f"❌ Failed to fetch users: {e}")
    sys.exit(1)

if not user_ids:
    print("ℹ️ No users found in database. Please log in first using your Telegram Bot (e.g. by running `/login`).")
    sys.exit(0)

print("\n--- Triggering Morning Notification Job (8:00 AM) ---")
try:
    morning_notification()
    print("✅ Morning notification job completed!")
except Exception as e:
    print(f"❌ Morning notification job failed: {e}")

print("\n--- Triggering Afternoon Notification Job (2:00 PM) ---")
try:
    afternoon_notification()
    print("✅ Afternoon notification job completed!")
except Exception as e:
    print(f"❌ Afternoon notification job failed: {e}")
