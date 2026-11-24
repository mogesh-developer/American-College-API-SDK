from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ..database.sqlite import get_credentials
from ..utils.session_manager import session_manager
from amc_api.exceptions import AMCException


def placement_inline_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📢 Job Vacancies", callback_data="place_vacancies"),
        InlineKeyboardButton("📝 My Applied Jobs", callback_data="place_applied")
    )
    return markup


def elective_inline_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📚 Available Electives", callback_data="elec_available"),
        InlineKeyboardButton("✅ My Selections", callback_data="elec_my")
    )
    return markup


def register_handlers(bot: TeleBot):

    # Placements
    @bot.message_handler(func=lambda msg: msg.text == "💼 Placements")
    def handle_placements(message: Message):
        creds = get_credentials(message.chat.id)
        if not creds:
            bot.send_message(message.chat.id, "Please `/login` first to view placements.")
            return

        bot.send_message(
            message.chat.id,
            "💼 **Campus Placements & Job Vacancies**\n\nExplore opportunities and track your applications:",
            parse_mode="Markdown",
            reply_markup=placement_inline_menu()
        )

    # Electives
    @bot.message_handler(func=lambda msg: msg.text == "📚 Electives")
    def handle_electives(message: Message):
        creds = get_credentials(message.chat.id)
        if not creds:
            bot.send_message(message.chat.id, "Please `/login` first to view electives.")
            return

        bot.send_message(
            message.chat.id,
            "📚 **Elective Course Registrations**\n\nView available and selected elective subjects:",
            parse_mode="Markdown",
            reply_markup=elective_inline_menu()
        )

    # Placement Callbacks
    @bot.callback_query_handler(func=lambda call: call.data.startswith("place_"))
    def handle_placement_callbacks(call: CallbackQuery):
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

        bot.answer_callback_query(call.id, "Loading placement data...")

        if call.data == "place_vacancies":
            try:
                jobs = client.placement_vacancies()
                if not jobs:
                    text = "ℹ️ No active campus job openings right now."
                else:
                    lines = ["📢 **Campus Job Vacancies:**\n"]
                    for j in jobs[:8]:
                        pkg = f" | Package: `{j.salary_package}`" if j.salary_package else ""
                        lines.append(f"🏢 **{j.company_name}** - `{j.job_title}`{pkg}\n  Deadline: `{j.last_date or 'N/A'}`")
                    text = "\n".join(lines)
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=placement_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Failed to fetch vacancies: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=placement_inline_menu())

        elif call.data == "place_applied":
            try:
                applied = client.placement_applied()
                if not applied:
                    text = "ℹ️ You haven't applied for any jobs yet."
                else:
                    lines = ["📝 **Your Applied Jobs:**\n"]
                    for j in applied:
                        lines.append(f"• **{j.company_name}** ({j.job_title})")
                    text = "\n".join(lines)
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=placement_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Failed to fetch applied list: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=placement_inline_menu())

    # Electives Callbacks
    @bot.callback_query_handler(func=lambda call: call.data.startswith("elec_"))
    def handle_elective_callbacks(call: CallbackQuery):
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

        bot.answer_callback_query(call.id, "Loading electives...")

        if call.data == "elec_available":
            try:
                subs = client.electives()
                if not subs:
                    text = "ℹ️ No elective courses open for registration."
                else:
                    lines = ["📚 **Available Electives:**\n"]
                    for s in subs[:10]:
                        lines.append(f"• `{s.subject_code}` - {s.subject_name}")
                    text = "\n".join(lines)
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=elective_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Failed to fetch electives: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=elective_inline_menu())

        elif call.data == "elec_my":
            try:
                selected = client.my_electives()
                if not selected:
                    text = "ℹ️ No electives currently selected."
                else:
                    lines = ["✅ **Your Selected Electives:**\n"]
                    for s in selected:
                        lines.append(f"• `{s.subject_code}` - {s.subject_name}")
                    text = "\n".join(lines)
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=elective_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Failed to fetch selection: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=elective_inline_menu())

