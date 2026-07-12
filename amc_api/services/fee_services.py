from ..core.base_service import BaseService
from ..models.fee_service_group import FeeServiceGroupsResponse
from .. import endpoints


class FeeServicesService(BaseService):

    def list_groups(self):

        data = self._post(
            endpoints.LIST_SERVICE_GROUPS
        )

        return FeeServiceGroupsResponse.from_dict(data)
