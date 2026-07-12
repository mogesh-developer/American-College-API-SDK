from amc_api import AMCClient
from ..database.sqlite import get_credentials, update_user_token
from .session_manager import session_manager


class UserNotRegistered(Exception):
    """Raised when the Telegram user is not registered in the local database."""
    pass


def get_client_for_user(telegram_id: int) -> AMCClient:

    creds = get_credentials(telegram_id)

    if not creds:
        raise UserNotRegistered("User not registered in database.")

    client = session_manager.get_client(
        telegram_id=telegram_id,
        reg_no=creds["reg_no"],
        dob=creds["dob"],
        token=creds.get("token")
    )

    # Set token update listener to keep SQLite up to date
    client.session.token_update_callback = lambda t: update_user_token(telegram_id, t)

    return client
