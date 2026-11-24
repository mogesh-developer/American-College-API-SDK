from ..core.base_service import BaseService
from ..core.response import APIResponse
from ..models.hallticket import HallTicket, HallTicketSubject
from .. import endpoints
from ..utils.parser import parse_many


class HallTicketService(BaseService):

    def get_hallticket(self):
        data = self._post(endpoints.HALLTICKET)
        return HallTicket.from_dict(data if isinstance(data, dict) else {"data": data})

    def subjects(self):
        data = self._post(endpoints.HALLTICKET_SUBJECTS)
        response = APIResponse(data)
        return parse_many(HallTicketSubject, response.data)

    def pdf_preview(self):
        data = self._post(endpoints.HALLTICKET_PDF_PREVIEW)
        response = APIResponse(data)
        return response.data

