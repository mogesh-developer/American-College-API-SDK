from ..core.base_service import BaseService
from ..core.response import APIResponse
from ..models.exam import InternalMark, ExamResultItem, ExamResult
from .. import endpoints
from ..utils.parser import parse_many


class ExamService(BaseService):

    def internal_marks(self, semester: str = None):
        payload = {}
        if semester:
            payload["semester"] = semester

        data = self._post(endpoints.INTERNAL_MARKS, payload if payload else None)
        response = APIResponse(data)
        return parse_many(InternalMark, response.data)

    def exam_months(self):
        data = self._post(endpoints.EXAM_MONTHS_LIST)
        response = APIResponse(data)
        return response.data

    def results(self, exam_month: str = None):
        payload = {}
        if exam_month:
            payload["exam_month"] = exam_month

        data = self._post(endpoints.EXAM_RESULT_DATA, payload if payload else None)
        return ExamResult.from_dict(data if isinstance(data, dict) else {"data": data})

    def results_list(self):
        data = self._post(endpoints.EXAM_RESULTS_LIST)
        response = APIResponse(data)
        return response.data

    def all_marks(self):
        data = self._post(endpoints.ALL_MARKS_LIST)
        response = APIResponse(data)
        return response.data

