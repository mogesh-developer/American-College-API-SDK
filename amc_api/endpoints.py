"""
All API endpoints used by the SDK.
"""


LOGIN = "/api/mob/stu/v1/login/check"

SETTINGS = "/api/v1/settings"

PROFILE = "/api/mob/stu/v2/profile"

ENROLLED_PROGRAMMES = "/api/mob/stu/v2/home/enrolled-programmes"

REGISTER_PROFILE = "/api/mob/stu/v1/register/profile"

ABSENT_DAYS = "/api/mob/stu/v2/timetable/my-absent-days"

TIMETABLE = "/api/mob/stu/v2/timetable/my-time-table"

TIMETABLE_DAY_VALUE = "/api/mob/stu/v2/timetable/day-value"

UPCOMING_DAY_ORDER = "/api/v1/oa/dayorder/upcoming-day-order"

ATTENDANCE = "/api/mob/stu/v2/attendance"

FULL_ATTENDANCE = "/api/mob/stu/v2/timetable/full-attendance"

SUBJECT_WISE_ATTENDANCE = "/api/mob/stu/v2/timetable/subject-wise-report"

FEES = "/api/mob/stu/v2/fees/my-fees"

LIST_SERVICE_GROUPS = "/api/mob/stu/v2/fee-services/list-service-groups"

NOTIFICATION = "/api/mob/stu/v2/notification"

NOTIFICATION_COUNT = "/api/mob/stu/v2/notification/notification-count"

NEWS = "/api/mob/stu/v1/news/list-news"

# Exam Results & Marks
INTERNAL_MARKS = "/api/mob/stu/v1/exam-results/internal-marks"
EXAM_RESULTS_LIST = "/api/mob/stu/v1/exam-results/list-results"
EXAM_RESULT_DATA = "/api/mob/stu/v1/exam-results/exam-result-data"
EXAM_MONTHS_LIST = "/api/mob/stu/v1/exam-results/exam-months-list"
ALL_MARKS_LIST = "/api/mob/stu/v1/exam-results/all-marks-list"

# Hall Ticket
HALLTICKET = "/api/mob/stu/v1/hallticket/my-hallticket"
HALLTICKET_SUBJECTS = "/api/mob/stu/v1/hallticket/hallticket-students-subject-list"
HALLTICKET_PDF_PREVIEW = "/api/mob/stu/v1/hallticket/hallticket-pdf-preview"

# Electives
ELECTIVE_LIST = "/api/mob/stu/v1/elective/list"
ELECTIVE_MY_SELECTION = "/api/mob/stu/v1/elective/my-selection-list"

# Placements
PLACEMENT_VACANCIES = "/api/mob/stu/v2/placement/job-vacancy-list"
PLACEMENT_APPLIED = "/api/mob/stu/v2/placement/applied-list"

# Syllabus & Bus
SYLLABUS_LIST = "/api/mob/stu/v2/timetable/syllabus-list"
BUS_GPS_URL = "/api/mob/stu/v1/bus/gps-url-new"

