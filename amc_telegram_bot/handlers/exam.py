import math
from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ..database.sqlite import get_credentials
from ..utils.session_manager import session_manager
from amc_api.exceptions import AMCException


def exam_inline_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 Internal Marks (CIA)", callback_data="exam_internals"),
        InlineKeyboardButton("🎯 Target Exam Marks", callback_data="exam_target_marks"),
        InlineKeyboardButton("🏆 Semester Results", callback_data="exam_results"),
        InlineKeyboardButton("📜 Available Exam Months", callback_data="exam_months"),
        InlineKeyboardButton("📑 All Marks Sheet", callback_data="exam_all_marks")
    )
    return markup



def register_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda msg: msg.text == "📝 Exam & Results")
    def handle_exam_menu(message: Message):
        creds = get_credentials(message.chat.id)
        if not creds:
            bot.send_message(message.chat.id, "Please `/login` first to view exam marks and results.")
            return

        bot.send_message(
            message.chat.id,
            "📝 **Examination & Academic Results**\n\nChoose an option below to fetch your marks:",
            parse_mode="Markdown",
            reply_markup=exam_inline_menu()
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("exam_"))
    def handle_exam_callbacks(call: CallbackQuery):
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

        bot.answer_callback_query(call.id, "Fetching exam data...")

        if call.data == "exam_internals":
            try:
                marks = client.internal_marks()
                if not marks:
                    text = "ℹ️ No continuous internal assessment marks found."
                else:
                    lines = ["📊 **Continuous Internal Assessment (CIA):**\n"]
                    for m in marks[:15]:
                        test = f" ({m.test_name})" if m.test_name else ""
                        max_m = f"/{m.max_mark}" if m.max_mark else ""
                        lines.append(f"• **{m.subject_code}** - {m.subject_name}\n  🎯 Mark: `{m.mark}{max_m}`{test}")
                    text = "\n".join(lines)
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=exam_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Failed to fetch internal marks: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=exam_inline_menu())

        elif call.data == "exam_results":
            try:
                res = client.exam_results()
                if not res.items:
                    text = "ℹ️ No semester exam results currently published."
                else:
                    lines = [f"🏆 **Semester Exam Results** (Month: {res.exam_month or 'Latest'}):\n"]
                    if res.gpa:
                        lines.append(f"🎖 **GPA:** `{res.gpa}` | **CGPA:** `{res.cgpa}`\n")
                    for it in res.items[:12]:
                        grade = f"Grade: {it.grade}" if it.grade else ""
                        lines.append(f"• **{it.subject_code}**: {it.subject_name}\n  Result: `{it.result or 'N/A'}` | {grade}")
                    text = "\n".join(lines)
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=exam_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Failed to fetch results: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=exam_inline_menu())

        elif call.data == "exam_months":
            try:
                months = client.exam_months()
                if not months:
                    text = "ℹ️ No exam sessions listed."
                else:
                    lines = ["📜 **Published Exam Sessions:**\n"]
                    if isinstance(months, list):
                        for m in months:
                            val = m.get("month") or m.get("exam_month") if isinstance(m, dict) else str(m)
                            lines.append(f"• `{val}`")
                    else:
                        lines.append(str(months))
                    text = "\n".join(lines)
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=exam_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Failed to fetch exam months: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=exam_inline_menu())

        elif call.data == "exam_target_marks":
            try:
                marks = client.internal_marks()
                if not marks:
                    text = "ℹ️ No continuous internal assessment (CIA) marks found to compute target scores."
                else:
                    lines = [
                        "🎯 **EXTERNAL EXAM TARGET SCORE PREDICTOR**",
                        "*(External Exam: 75 Marks | Pass: 30/75 & 40/100 Total)*\n"
                    ]
                    for m in marks[:10]:
                        try:
                            cia = float(m.mark) if m.mark and m.mark.replace(".", "", 1).isdigit() else None
                        except ValueError:
                            cia = None

                        if cia is not None:
                            # Pass condition: External >= 30, Total (CIA + Ext) >= 40
                            pass_target = max(30, math.ceil(40 - cia))
                            # First class / A Grade condition: Total >= 60
                            first_class = max(30, math.ceil(60 - cia))
                            # Distinction / O Grade condition: Total >= 75
                            distinction = max(30, math.ceil(75 - cia))

                            fc_str = f"`{first_class}/75`" if first_class <= 75 else "N/A"
                            dist_str = f"`{distinction}/75`" if distinction <= 75 else "N/A"

                            lines.append(
                                f"• **{m.subject_code}** (CIA: `{cia}/25`)\n"
                                f"  ↳ 🎯 To Pass: `{pass_target}/75` | First Class: {fc_str} | Distinction: {dist_str}"
                            )
                        else:
                            lines.append(f"• **{m.subject_code}** - Marks pending")
                    text = "\n".join(lines)
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=exam_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Failed to calculate target marks: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=exam_inline_menu())

        elif call.data == "exam_all_marks":

            try:
                all_m = client.all_marks()
                text = "📑 **All Marks History:**\n\nFetched successfully from portal."
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=exam_inline_menu())
            except AMCException as e:
                bot.edit_message_text(f"❌ Failed to fetch marks history: {e}", chat_id=chat_id, message_id=call.message.message_id, reply_markup=exam_inline_menu())

