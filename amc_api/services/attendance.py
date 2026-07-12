from ..core.base_service import BaseService
from ..core.response import APIResponse
from ..models.attendance import Attendance
from .. import endpoints
from ..utils.parser import parse_many


class AttendanceService(BaseService):

    def absent_days(self):

        data = self._post(
            endpoints.ABSENT_DAYS,
            {
                "type": "absent"
            }
        )

        response = APIResponse(data)

        return parse_many(
            Attendance,
            response.data
        )

