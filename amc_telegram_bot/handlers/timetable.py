from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ..utils.sdk_helper import get_client_for_user, UserNotRegistered
from amc_api.exceptions import LoginError, AMCException
from datetime import datetime
from ..database.sqlite import get_weekly_timetable


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


def format_schedule_from_api(tt_obj):
    """
    Format schedule dynamically from college API Timetable response object.
    """
    if tt_obj.is_holiday:
        h_name = tt_obj.holiday.holiday_name if tt_obj.holiday else "Holiday"
        return f"🏖️ *Today is a Holiday / No Class Scheduled:* `{h_name}` 🏖️\n\n"

    if not tt_obj.schedule:
        return "ℹ️ *No classes scheduled for today in the portal.* 🏖️\n\n"

    lines = ["📝 *Today's Portal Schedule:*\n"]
    for item in tt_obj.schedule:
        sub_name = item.subject_name or (f"Subject #{item.subject_id}" if item.subject_id else "Class")
        staff = f" | `{item.teacher_name}`" if item.teacher_name else ""
        lines.append(f"🕒 *Hour {item.hour}:* **{sub_name}**{staff}\n")

    return "\n".join(lines) + "\n"


def format_day_order_message(day_order, schedule):
    text = (
        f"📅 *TIME TABLE: {day_order}* 📅\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    if not schedule:
        text += "ℹ️ *No predefined timetable entries found for this day order.*\n\n"
    else:
        for entry in schedule:
            code = f"`{entry['code']}` " if entry.get("code") else ""
            staff = f" | `{entry['staff']}`" if entry.get("staff") else ""
            text += (
                f"🕒 *Hour {entry['hour']}:* {code}\n"
                f"  ↳ *{entry.get('name') or 'Subject'}*{staff}\n\n"
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

        loading_msg = bot.send_message(message.chat.id, "🔄 *Loading timetable from college portal...*", parse_mode="Markdown")

        try:
            # 1. Fetch live dynamic day order and status from portal API
            day_val_str = "Unknown"
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

            # 2. Fetch live dynamic schedule directly from the portal
            schedule_added = False
            try:
                tt = client.timetable(type_str="today")
                if tt:
                    text += format_schedule_from_api(tt)
                    schedule_added = True
            except Exception:
                pass

            # Fallback to day order lookup from database if portal schedule is empty and day_key exists
            if not schedule_added and day_val_str not in ("Holiday", "Unknown"):
                num = day_val_str.split(" ")[-1]
                day_key = f"D{num}" if num.isdigit() else None
                if day_key:
                    db_sched = get_weekly_timetable(day_key)
                    if db_sched:
                        text += f"📝 *Today's Schedule ({day_key}):*\n\n"
                        for entry in db_sched:
                            code = f"`{entry['code']}` " if entry.get("code") else ""
                            staff = f" | `{entry['staff']}`" if entry.get("staff") else ""
                            text += f"🕒 *Hour {entry['hour']}:* {code}\n  ↳ *{entry.get('name')}*{staff}\n\n"

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
