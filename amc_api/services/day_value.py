from ..core.base_service import BaseService
from ..models.day_value import DayValue
from .. import endpoints


class DayValueService(BaseService):

    def get(self):

        data = self._get(
            endpoints.TIMETABLE_DAY_VALUE
        )

        return DayValue.from_dict(data)
