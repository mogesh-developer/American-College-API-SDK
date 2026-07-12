from ..core.base_service import BaseService
from ..models.fees import Fees
from .. import endpoints


class FeesService(BaseService):

    def get(self, balance_only: bool = False):

        payload = {
            "balance_only": "1" if balance_only else "0"
        }

        data = self._post(
            endpoints.FEES,
            data=payload
        )

        return Fees.from_dict(data)