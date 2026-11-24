import math
from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ..utils.sdk_helper import get_client_for_user, UserNotRegistered
from ..database.sqlite import get_credentials
from amc_api.exceptions import AMCException


def calculate_bunk_margin(present: int, total: int, target_pct: float = 75.0):
    """
    Calculates:
    - If current percentage >= target_pct: how many classes can be skipped safely.
    - If current percentage < target_pct: how many consecutive classes must be attended to reach target_pct.
    """
    if total <= 0:
        return {"status": "no_data", "safe_bunks": 0, "needed_classes": 0, "pct": 0.0}

    pct = (present / total) * 100.0
    target_ratio = target_pct / 100.0

    if pct >= target_pct:
        # present / (total + x) >= target_ratio
        # total + x <= present / target_ratio
        # x <= (present / target_ratio) - total
        safe_bunks = math.floor((present / target_ratio) - total)
        return {
            "status": "safe",
            "safe_bunks": max(0, safe_bunks),
            "needed_classes": 0,
            "pct": round(pct, 1)
        }
    else:
        # (present + y) / (total + y) >= target_ratio
        # present + y >= target_ratio * total + target_ratio * y
        # y * (1 - target_ratio) >= target_ratio * total - present
        needed = math.ceil((target_ratio * total - present) / (1 - target_ratio))
        return {
            "status": "critical",
            "safe_bunks": 0,
            "needed_classes": max(0, needed),
            "pct": round(pct, 1)
        }


def calculator_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 Refresh Calculator", callback_data="calc_bunk_refresh")
    )
    return markup


def register_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda msg: msg.text in ("🧮 Bunk Calculator", "/calculator", "/bunk"))
    def handle_bunk_calculator(message: Message):
        chat_id = message.chat.id
        creds = get_credentials(chat_id)
        if not creds:
            bot.send_message(chat_id, "Please `/login` first to calculate your attendance margin.")
            return

        loading_msg = bot.send_message(chat_id, "🔄 *Calculating attendance margins from live portal data...*", parse_mode="Markdown")

        try:
            client = get_client_for_user(chat_id)
            subjects = client.subject_wise_attendance()
            if not subjects:
                bot.edit_message_text(
                    "ℹ️ No subject attendance data recorded in the portal.",
                    chat_id=chat_id,
                    message_id=loading_msg.message_id
                )
                return

            lines = [
                "🧮 *SMART ATTENDANCE & BUNK CALCULATOR (75% Target)*",
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            ]

            total_present = 0
            total_hours = 0

            for sub in subjects:
                present = int(sub.total_hours_present)
                total = int(sub.total_hours)
                total_present += present
                total_hours += total

                calc = calculate_bunk_margin(present, total, target_pct=75.0)
                sub_label = sub.subject_code or sub.subject_name

                if calc["status"] == "safe":
                    bunks = calc["safe_bunks"]
                    if bunks > 0:
                        status_str = f"🟢 *{calc['pct']}%* — Can safely miss *{bunks}* class{'es' if bunks > 1 else ''}"
                    else:
                        status_str = f"🟡 *{calc['pct']}%* — On the line! Do not miss next class."
                else:
                    needed = calc["needed_classes"]
                    status_str = f"🔴 *{calc['pct']}%* — Must attend *{needed}* class{'es' if needed > 1 else ''} consecutively!"

                lines.append(f"• **{sub_label}**\n  ↳ {status_str}\n")

            overall = calculate_bunk_margin(total_present, total_hours, target_pct=75.0)
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
            if overall["status"] == "safe":
                lines.append(f"🎯 *Overall:* `{overall['pct']}%` (Buffer: *{overall['safe_bunks']}* hours)\n")
            else:
                lines.append(f"⚠️ *Overall:* `{overall['pct']}%` (Need *{overall['needed_classes']}* hours consecutively)\n")

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=loading_msg.message_id,
                text="\n".join(lines),
                parse_mode="Markdown",
                reply_markup=calculator_keyboard()
            )

        except AMCException as e:
            bot.edit_message_text(f"❌ Failed to fetch attendance: {e}", chat_id=chat_id, message_id=loading_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Error: {str(e)}", chat_id=chat_id, message_id=loading_msg.message_id)

    @bot.callback_query_handler(func=lambda call: call.data == "calc_bunk_refresh")
    def handle_bunk_refresh(call: CallbackQuery):
        bot.answer_callback_query(call.id, "Refreshing margins...")
        handle_bunk_calculator(call.message)
