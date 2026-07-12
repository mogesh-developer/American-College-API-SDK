from ..core.base_service import BaseService
from ..core.response import APIResponse
from ..models.news import NewsItem
from .. import endpoints
from ..utils.parser import parse_many


class NewsService(BaseService):

    def list(self, type_str: str = "announcement", mobile_popup: bool = True):

        payload = {
            "type": type_str,
            "mobile_popup": "1" if mobile_popup else "0"
        }

        data = self._post(
            endpoints.NEWS,
            data=payload
        )

        response = APIResponse(data)

        return parse_many(
            NewsItem,
            response.data
        )