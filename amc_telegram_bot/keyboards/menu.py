from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    markup.add(
        KeyboardButton("🎓 Profile"), KeyboardButton("📊 Attendance"),
        KeyboardButton("🧮 Bunk Calculator"), KeyboardButton("📅 Timetable"),
        KeyboardButton("📝 Exam & Results"), KeyboardButton("🎟️ Hall Ticket"),
        KeyboardButton("💰 Fees"), KeyboardButton("💼 Placements"),
        KeyboardButton("📚 Electives"), KeyboardButton("🔔 Notifications"),
        KeyboardButton("📰 News"), KeyboardButton("🔄 Clear Cache"),
        KeyboardButton("⚙️ Settings"), KeyboardButton("🔓 Logout")
    )

    return markup



