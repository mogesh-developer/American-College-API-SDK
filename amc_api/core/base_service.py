from .. import endpoints
from ..exceptions import APIError


class BaseService:

    def __init__(self, session):
        self.session = session

    def _post(self, endpoint, data=None):

        response = self.session.post(
            self.session.config.base_url + endpoint,
            data=data
        )

        if response.status_code != 200:
            raise APIError(
                f"HTTP {response.status_code}"
            )

        result = response.json()

        return result

    def _get(self, endpoint, params=None):

        response = self.session.get(
            self.session.config.base_url + endpoint,
            params=params
        )

        if response.status_code != 200:
            raise APIError(
                f"HTTP {response.status_code}"
            )

        result = response.json()

        return result

