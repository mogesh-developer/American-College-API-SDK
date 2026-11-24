from amc_api import AMCClient, Config


# Global snappy in-memory cache for attendance
attendance_cache = {}


class SessionManager:

    def __init__(self):
        self._clients = {}

    def get_client(self, telegram_id: int, reg_no: str, dob: str, token: str = None) -> AMCClient:

        client = self._clients.get(telegram_id)
        if not client or client.reg_no != reg_no or client.dob != dob:
            config = Config(enable_logging=True)
            client = AMCClient(
                reg_no=reg_no,
                dob=dob,
                token=token,
                config=config
            )
            self._clients[telegram_id] = client
            # Clear stale attendance cache
            if telegram_id in attendance_cache:
                del attendance_cache[telegram_id]
        elif token and client.session.api_token != token:
            client.session.set_token(token)

        return self._clients[telegram_id]

    def remove_client(self, telegram_id: int):

        if telegram_id in self._clients:
            del self._clients[telegram_id]
        # Clear stale attendance cache
        if telegram_id in attendance_cache:
            del attendance_cache[telegram_id]


session_manager = SessionManager()


