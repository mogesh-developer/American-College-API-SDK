from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ..database.sqlite import get_credentials
from ..utils.session_manager import session_manager
from amc_api.exceptions import AMCException


def hallticket_inline_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎫 My Hall Ticket", callback_data="ht_view"),
        InlineKeyboardButton("📋 Exam Subjects", callback_data="ht_subjects")
    )
    return markup


def register_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda msg: msg.text == "🎟️ Hall Ticket")
    def handle_hallticket(message: Message):
        creds = get_credentials(message.chat.id)
        if not creds:
            bot.send_message(message.chat.id, "Please `/login` first to view your hall ticket.")
            return

        bot.send_message(
            message.chat.id,
            "🎟️ **Examination Hall Ticket**\n\nCheck your exam dates, timings, and seat numbers:",
            parse_mode="Markdown",
            reply_markup=hallticket_inline_menu()
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("ht_"))
    def handle_ht_callbacks(call: CallbackQuery):
        chat_id = call.message.chat.id
        creds = get_credentials(chat_id)
        if not creds:
            bot.answer_callback_query(call.id, "Please login first.")
            return

        client = session_manager.get_client(
            telegram_id=chat_id,
            reg_no=creds["reg_no"],
            dob=creds["dob"],
            token=creds.get("token")
        )

        bot.answer_callback_query(call.id, "Fetching hall ticket...")

        if call.data == "ht_view":
            try:
                ticket = client.hallticket()
                lines = [f"🎟️ **Hall Ticket for {ticket.student_name or creds['reg_no']}**\n"]
                if ticket.exam_name:
                    lines.append(f"📌 Exam: `{ticket.exam_name}`\n")
                if not ticket.subjects:
                    lines.append("ℹ️ No scheduled exam sessions on hall ticket.")
                else:
                    for s in ticket.subjects:
                        lines.append(f"• **{s.subject_code}** - {s.subject_name}\n  📅 Date: `{s.exam_date or 'TBA'}` | Session: `{s.session or 'TBA'}` | Hall: `{s.hall_name or 'TBA'}`")
                bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=hallticket_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Unable to load hall ticket: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=hallticket_inline_menu())

        elif call.data == "ht_subjects":
            try:
                subs = client.hallticket_subjects()
                if not subs:
                    text = "ℹ️ No hall ticket subjects registered."
                else:
                    lines = ["📋 **Hall Ticket Registered Subjects:**\n"]
                    for s in subs:
                        lines.append(f"• **{s.subject_code}**: {s.subject_name}\n  Date: `{s.exam_date or 'TBA'}`")
                    text = "\n".join(lines)
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=hallticket_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Failed to fetch subjects: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=hallticket_inline_menu())

