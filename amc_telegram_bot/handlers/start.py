from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardRemove
from ..database.sqlite import get_credentials, save_credentials, delete_credentials
from ..keyboards.menu import main_menu
from ..utils.session_manager import session_manager
from amc_api import AMCClient, Config
from amc_api.exceptions import LoginError


def register_handlers(bot: TeleBot):

    @bot.message_handler(commands=["start", "help"])
    def cmd_start(message: Message):

        creds = get_credentials(message.chat.id)

        if creds:
            bot.send_message(
                message.chat.id,
                f"Welcome back! You are logged in with Register No: {creds['reg_no']}.\nUse the menu buttons below to fetch information.",
                reply_markup=main_menu()
            )
        else:
            bot.send_message(
                message.chat.id,
                "Welcome to 🎓 AMC Student Bot!\n\nYou are not logged in yet. Please use `/login` to register your credentials.",
                reply_markup=ReplyKeyboardRemove()
            )

    @bot.message_handler(commands=["login"])
    def cmd_login(message: Message):

        msg = bot.send_message(message.chat.id, "Please enter your Register Number:")
        bot.register_next_step_handler(msg, process_reg_no)

    def process_reg_no(message: Message):

        reg_no = message.text.strip()

        msg = bot.send_message(message.chat.id, "Please enter your Date of Birth (YYYY-MM-DD):")
        bot.register_next_step_handler(msg, process_dob, reg_no)

    def process_dob(message: Message, reg_no: str):

        dob = message.text.strip()
        loading_msg = bot.send_message(message.chat.id, "Checking credentials and logging in...")

        try:
            config = Config(enable_logging=True)
            client = AMCClient(reg_no=reg_no, dob=dob, config=config)

            # Save credentials & Cache client instance
            save_credentials(message.chat.id, reg_no, dob)
            from ..database.sqlite import update_user_token
            if client.session.api_token:
                update_user_token(message.chat.id, client.session.api_token)
            session_manager._clients[message.chat.id] = client

            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=loading_msg.message_id,
                text=f"Login successful! Welcome, {client.profile().student_name}."
            )
            bot.send_message(
                message.chat.id,
                "Use the menu buttons below to access your portal resources:",
                reply_markup=main_menu()
            )
        except LoginError:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=loading_msg.message_id,
                text="Login failed. Invalid Register Number or DOB. Please try `/login` again."
            )
        except Exception as e:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=loading_msg.message_id,
                text=f"An error occurred during login: {str(e)}. Please try `/login` again."
            )

    @bot.message_handler(func=lambda msg: msg.text in ("🔓 Logout", "/logout"))
    def cmd_logout(message: Message):

        delete_credentials(message.chat.id)
        session_manager.remove_client(message.chat.id)
        bot.send_message(
            message.chat.id,
            "Logged out successfully. Credentials cleared from database.",
            reply_markup=ReplyKeyboardRemove()
        )
