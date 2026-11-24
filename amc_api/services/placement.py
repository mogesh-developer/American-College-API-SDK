from ..core.base_service import BaseService
from ..core.response import APIResponse
from ..models.placement import PlacementJob
from .. import endpoints
from ..utils.parser import parse_many


class PlacementService(BaseService):

    def vacancies(self):
        data = self._post(endpoints.PLACEMENT_VACANCIES)
        response = APIResponse(data)
        return parse_many(PlacementJob, response.data)

    def applied_jobs(self):
        data = self._post(endpoints.PLACEMENT_APPLIED)
        response = APIResponse(data)
        return parse_many(PlacementJob, response.data)

