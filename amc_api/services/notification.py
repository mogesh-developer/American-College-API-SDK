from ..core.base_service import BaseService
from ..models.notification import NotificationCount
from .. import endpoints


class NotificationService(BaseService):

    def get_count(self, uuid: str, course: int, type_str: str = "student"):

        payload = {
            "type": type_str,
            "uuid": uuid,
            "course": str(course)
        }

        data = self._post(
            endpoints.NOTIFICATION_COUNT,
            data=payload
        )

        return NotificationCount.from_dict(data)