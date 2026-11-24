from .. import endpoints
from ..exceptions import APIError


class BaseService:

    def __init__(self, session):
        self.session = session

    def post(self, endpoint: str, data=None):

        response = self.session.post(
            endpoints.BASE_URL + endpoint,
            data=data
        )

        if response.status_code != 200:
            raise APIError(
                f"HTTP {response.status_code}"
            )

        result = response.json()

        if isinstance(result, dict):

            if result.get("status") == "0":
                raise APIError(result.get("message"))

            if result.get("errorcode") == "401":
                raise APIError("Unauthorized")

        return result