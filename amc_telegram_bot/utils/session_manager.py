from amc_api import AMCClient, Config


class SessionManager:

    def __init__(self):
        self._clients = {}

    def get_client(self, telegram_id: int, reg_no: str, dob: str, token: str = None) -> AMCClient:

        if telegram_id not in self._clients:
            config = Config(enable_logging=True)
            self._clients[telegram_id] = AMCClient(
                reg_no=reg_no,
                dob=dob,
                token=token,
                config=config
            )
        return self._clients[telegram_id]

    def remove_client(self, telegram_id: int):

        if telegram_id in self._clients:
            del self._clients[telegram_id]


session_manager = SessionManager()
