from ..core.base_service import BaseService
from ..models.programme import EnrolledProgrammes
from .. import endpoints


class ProgrammeService(BaseService):

    def enrolled(self):

        data = self._post(
            endpoints.ENROLLED_PROGRAMMES
        )

        return EnrolledProgrammes.from_dict(data)
