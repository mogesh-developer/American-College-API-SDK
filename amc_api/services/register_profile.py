from ..core.base_service import BaseService
from ..core.response import APIResponse
from ..models.register_profile import RegisterProfile
from .. import endpoints
from ..utils.parser import parse


class RegisterProfileService(BaseService):

    def get(self, uuid: str, register_no: str):

        payload = {
            "uuid": uuid,
            "registerno": register_no
        }

        data = self._post(
            endpoints.REGISTER_PROFILE,
            data=payload
        )

        response = APIResponse(data)

        return parse(
            RegisterProfile,
            response.data
        )
