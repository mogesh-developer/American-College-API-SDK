from ..core.base_service import BaseService
from ..core.response import APIResponse
from ..models.day_order import DayOrder
from .. import endpoints
from ..utils.parser import parse


class DayOrderService(BaseService):

    def upcoming(self):

        data = self._get(
            endpoints.UPCOMING_DAY_ORDER
        )

        response = APIResponse(data)

        return parse(
            DayOrder,
            response.data
        )
