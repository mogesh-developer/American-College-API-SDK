from ..core.base_service import BaseService
from ..models.timetable import Timetable
from .. import endpoints


class TimetableService(BaseService):

    def get(self, type_str: str = "today"):

        payload = {
            "type": type_str,
            "format_2": "1"
        }

        data = self._post(
            endpoints.TIMETABLE,
            data=payload
        )

        return Timetable.from_dict(data)
