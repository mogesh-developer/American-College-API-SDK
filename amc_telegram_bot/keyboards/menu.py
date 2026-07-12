from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    markup.add(
        KeyboardButton("🎓 Profile"), KeyboardButton("📊 Attendance"),
        KeyboardButton("📅 Timetable"), KeyboardButton("💰 Fees"),
        KeyboardButton("🔔 Notifications"), KeyboardButton("📰 News"),
        KeyboardButton("⚙️ Settings"), KeyboardButton("🔓 Logout")
    )

    return markup
