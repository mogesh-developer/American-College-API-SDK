from .session import AMCSession
from .exceptions import LoginError
from . import endpoints


class AMCAuth:

    def __init__(self, session: AMCSession):

        self.session = session

    def login(self, reg_no: str, dob: str):

        payload = {
            "student_status": "admitted",
            "fgh_dkv": "",
            "registerno": reg_no,
            "dob": dob
        }

        response = self.session.post(
            self.session.config.base_url + endpoints.LOGIN,
            data=payload
        )
        if response.status_code != 200:
            raise LoginError(f"HTTP {response.status_code}: Login failed")

        data = response.json()

        if data.get("errorcode") != "200":
            raise LoginError("Invalid Register Number or DOB")

        token = data["api"]

        self.session.set_token(token)

        return data
