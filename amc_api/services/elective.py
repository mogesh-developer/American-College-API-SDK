from ..core.base_service import BaseService
from ..core.response import APIResponse
from ..models.elective import ElectiveSubject
from .. import endpoints
from ..utils.parser import parse_many


class ElectiveService(BaseService):

    def list_electives(self):
        data = self._post(endpoints.ELECTIVE_LIST)
        response = APIResponse(data)
        return parse_many(ElectiveSubject, response.data)

    def my_selection(self):
        data = self._post(endpoints.ELECTIVE_MY_SELECTION)
        response = APIResponse(data)
        return parse_many(ElectiveSubject, response.data)

