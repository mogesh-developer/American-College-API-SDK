from ..core.base_service import BaseService
from ..models.settings import Settings
from .. import endpoints


class SettingsService(BaseService):

    def get(self, sta: int = 1):

        params = {
            "sta": str(sta)
        }

        data = self._get(
            endpoints.SETTINGS,
            params=params
        )

        return Settings.from_dict(data)
