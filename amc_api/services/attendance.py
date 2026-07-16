from ..core.base_service import BaseService
from ..core.response import APIResponse
from ..models.attendance import Attendance, FullAttendance, SubjectAttendance
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

    def full_attendance(self):

        data = self._post(
            endpoints.FULL_ATTENDANCE
        )

        return FullAttendance.from_dict(data)

    def subject_wise_report(self):

        data = self._post(
            endpoints.SUBJECT_WISE_ATTENDANCE
        )

        response = APIResponse(data)

        return parse_many(
            SubjectAttendance,
            response.data
        )



