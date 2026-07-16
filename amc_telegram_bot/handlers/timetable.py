from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ..utils.sdk_helper import get_client_for_user, UserNotRegistered
from amc_api.exceptions import LoginError
from datetime import datetime
from ..database.sqlite import get_cached_day_order, get_weekly_timetable, save_day_order


def get_day_order_keyboard():

    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("D1", callback_data="timetable_D1"),
        InlineKeyboardButton("D2", callback_data="timetable_D2"),
        InlineKeyboardButton("D3", callback_data="timetable_D3"),
        InlineKeyboardButton("D4", callback_data="timetable_D4"),
        InlineKeyboardButton("D5", callback_data="timetable_D5"),
        InlineKeyboardButton("D6", callback_data="timetable_D6"),
    )
    return markup


def format_day_order_message(day_order, schedule):

    text = (
        f"📅 *TIME TABLE: {day_order}* 📅\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    for entry in schedule:
        text += (
            f"🕒 *Hour {entry['hour']}:* `{entry['code']}`\n"
            f"  ↳ *{entry['name']}* | `{entry['staff']}`\n\n"
        )
    text += (
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔍 *Select a Day Order below to view its schedule:*"
    )
    return text


def register_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda msg: msg.text in ("📅 Timetable", "/timetable"))
    def cmd_timetable(message: Message):

        try:
            # Check user login registration locally
            client = get_client_for_user(message.chat.id)
        except UserNotRegistered:
            bot.send_message(message.chat.id, "❌ *Access Denied.*\nPlease login first using /login.", parse_mode="Markdown")
            return
        except LoginError:
            bot.send_message(message.chat.id, "❌ *Authentication Error.*\nYour stored credentials seem to be invalid. Please login again using /login.", parse_mode="Markdown")
            return
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ *Connection Error:*\nUnable to reach the college portal: `{str(e)}`", parse_mode="Markdown")
            return

        loading_msg = bot.send_message(message.chat.id, "🔄 *Loading timetable...*", parse_mode="Markdown")

        try:
            # Fetch day order status directly from college portal
            day_val_str = "Holiday"
            try:
                day_val_obj = client.timetable_day_value()
                if day_val_obj:
                    if day_val_obj.is_holiday:
                        day_val_str = "Holiday"
                    elif day_val_obj.day_order_text:
                        day_val_str = f"Day Order {day_val_obj.day_order_text}"
            except Exception:
                pass

            text = (
                "📅 *TIMETABLE & SCHEDULE REPORT*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📅 *Date:* `{datetime.now().strftime('%d-%m-%Y')}`\n"
                f"ℹ️ *Status:* `{day_val_str}`\n\n"
            )

            # Map e.g. "Day Order 3" or "3" to "D3"
            day_key = None
            if day_val_str.startswith("Day Order "):
                num = day_val_str.split(" ")[-1]
                day_key = f"D{num}"
            elif day_val_str.isdigit():
                day_key = f"D{day_val_str}"

            if day_key:
                schedule = get_weekly_timetable(day_key)
                if schedule:
                    text += f"📝 *Today's Schedule ({day_key}):*\n\n"
                    for entry in schedule:
                        text += (
                            f"🕒 *Hour {entry['hour']}:* `{entry['code']}`\n"
                            f"  ↳ *{entry['name']}* | `{entry['staff']}`\n\n"
                        )
            else:
                text += "🏖️ *Today is a Holiday / No Class Scheduled.* 🏖️\n\n"

            text += (
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔍 *Select a Day Order below to view its schedule:*"
            )

            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=loading_msg.message_id,
                text=text,
                reply_markup=get_day_order_keyboard(),
                parse_mode="Markdown"
            )
        except Exception as e:
            text = (
                "📅 *TIMETABLE & SCHEDULE REPORT*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"❌ *Error loading timetable:* `{str(e)}`\n\n"
                "🔍 *Select a Day Order below to view its schedule:*"
            )
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=loading_msg.message_id,
                text=text,
                reply_markup=get_day_order_keyboard(),
                parse_mode="Markdown"
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("timetable_"))
    def handle_timetable_callback(call):

        day_order = call.data.split("_")[1]
        schedule = get_weekly_timetable(day_order)

        if schedule:
            text = format_day_order_message(day_order, schedule)

            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=text,
                    reply_markup=get_day_order_keyboard(),
                    parse_mode="Markdown"
                )
            except Exception:
                pass
