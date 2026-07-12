from .config import Config
from .session import AMCSession
from .auth import AMCAuth

from .services.attendance import AttendanceService
from .services.fees import FeesService
from .services.timetable import TimetableService
from .services.register_profile import RegisterProfileService
from .services.settings import SettingsService
from .services.day_order import DayOrderService
from .services.notification import NotificationService
from .services.news import NewsService
from .services.day_value import DayValueService
from .services.fee_services import FeeServicesService
from .services.programme import ProgrammeService


class AMCClient:

    def __init__(
        self,
        reg_no: str,
        dob: str,
        token: str = None,
        config: Config = None
    ):

        self.reg_no = reg_no
        self.dob = dob
        self.config = config or Config()

        if self.config.enable_logging:
            from .logger import setup_logger
            setup_logger()

        self.session = AMCSession(self.config)

        self.auth = AMCAuth(self.session)

        # Set re-auth callback for session retry logic
        self.session.reauth_callback = lambda: self.auth.login(self.reg_no, self.dob)

        if token:
            self.session.set_token(token)
            self.user = None
        else:
            self.user = self.auth.login(self.reg_no, self.dob)

        # Services
        self.attendance_service = AttendanceService(self.session)
        self.fees_service = FeesService(self.session)
        self.timetable_service = TimetableService(self.session)
        self.register_profile_service = RegisterProfileService(self.session)
        self.settings_service = SettingsService(self.session)
        self.day_order_service = DayOrderService(self.session)
        self.notification_service = NotificationService(self.session)
        self.news_service = NewsService(self.session)
        self.day_value_service = DayValueService(self.session)
        self.fee_services_service = FeeServicesService(self.session)
        self.programme_service = ProgrammeService(self.session)

    def profile(self):

        from .models.profile import Profile
        if not self.user or "data" not in self.user:
            self.user = self.auth.login(self.reg_no, self.dob)
        return Profile.from_dict(self.user["data"])

    # --------------------
    # Attendance
    # --------------------

    def absent_days(self):

        return self.attendance_service.absent_days()

    # --------------------
    # Fees
    # --------------------

    def fees(self, balance_only: bool = False):

        return self.fees_service.get(balance_only=balance_only)

    # --------------------
    # Timetable
    # --------------------

    def timetable(self, type_str: str = "today"):

        return self.timetable_service.get(type_str=type_str)

    # --------------------
    # Timetable Day Value
    # --------------------

    def timetable_day_value(self):

        return self.day_value_service.get()

    # --------------------
    # Register Profile
    # --------------------

    def register_profile(self, uuid: str = None, register_no: str = None):

        if not uuid and self.user and "data" in self.user:
            uuid = self.user["data"].get("uuid")

        if not register_no and self.user and "data" in self.user:
            register_no = self.user["data"].get("registerno") or self.user["data"].get("admissionno")

        return self.register_profile_service.get(
            uuid=uuid,
            register_no=register_no
        )

    # --------------------
    # Settings
    # --------------------

    def settings(self, sta: int = 1):

        return self.settings_service.get(sta=sta)

    # --------------------
    # Day Order
    # --------------------

    def upcoming_day_order(self):

        return self.day_order_service.upcoming()

    # --------------------
    # Notifications
    # --------------------

    def notification_count(self, uuid: str = None, course: int = None, type_str: str = "student"):

        if not uuid and self.user and "data" in self.user:
            uuid = self.user["data"].get("uuid")

        if not course and self.user and "data" in self.user:
            course = self.user["data"].get("course")

        return self.notification_service.get_count(
            uuid=uuid,
            course=course,
            type_str=type_str
        )

    # --------------------
    # News
    # --------------------

    def news(self, type_str: str = "announcement", mobile_popup: bool = True):

        return self.news_service.list(type_str=type_str, mobile_popup=mobile_popup)

    # --------------------
    # Fee Services
    # --------------------

    def fee_service_groups(self):

        return self.fee_services_service.list_groups()

    # --------------------
    # Enrolled Programmes
    # --------------------

    def enrolled_programmes(self):

        return self.programme_service.enrolled()