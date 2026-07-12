from ..core.base_service import BaseService
from ..core.response import APIResponse
from ..models.profile import Profile
from .. import endpoints
from ..utils.parser import parse


class ProfileService(BaseService):

    def get(self):

        data = self._post(
            endpoints.PROFILE
        )

        response = APIResponse(data)

        return parse(
            Profile,
            response.data
        )


