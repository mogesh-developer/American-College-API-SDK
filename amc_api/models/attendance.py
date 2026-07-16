from dataclasses import dataclass
from typing import List, Optional


@dataclass(slots=True)
class Attendance:

    id: int
    date: str
    hour: int
    subject_id: int
    teacher_id: int
    leave_type: str
    status: int

    @classmethod
    def from_dict(cls, data):

        return cls(
            id=data["id"],
            date=data["attendance_date"],
            hour=data["hour_value"],
            subject_id=data["subject"],
            teacher_id=data["teacher"],
            leave_type=data["leave_type"],
            status=data["status"]
        )


@dataclass(slots=True)
class FullAttendanceRecord:
    attendance_date: str
    attendance_time: str
    day_value: int
    hour_value: int
    leave_type: str
    subject_id: int
    subject_code: str
    subject_name: str
    teacher_id: int
    teacher_name: str
    leave_remarks: Optional[str] = None
    part: Optional[int] = None
    short_name: Optional[str] = None
    student_uuid: Optional[str] = None
    subject_type: Optional[str] = None
    subject_virtual_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            attendance_date=data.get("attendance_date"),
            attendance_time=data.get("attendance_time"),
            day_value=data.get("day_value"),
            hour_value=data.get("hour_value"),
            leave_type=data.get("leave_type"),
            subject_id=data.get("subject"),
            subject_code=data.get("subject_code"),
            subject_name=data.get("subject_name"),
            teacher_id=data.get("teacher"),
            teacher_name=data.get("teacher_name"),
            leave_remarks=data.get("leave_remarks"),
            part=data.get("part"),
            short_name=data.get("short_name"),
            student_uuid=data.get("student_uuid"),
            subject_type=data.get("subject_type"),
            subject_virtual_name=data.get("subject_virtual_name")
        )


@dataclass(slots=True)
class DayOrderTimetableItem:
    hour_value: int
    subject_id: Optional[int]
    subject_code: Optional[str]
    subject_name: Optional[str]
    teacher_id: Optional[int]
    teacher_name: Optional[str]
    course: Optional[int] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    day_value: Optional[int] = None
    short_name: Optional[str] = None
    degree_name: Optional[str] = None
    course_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            hour_value=data.get("hour_value"),
            subject_id=data.get("subject"),
            subject_code=data.get("subject_code"),
            subject_name=data.get("subject_name"),
            teacher_id=data.get("teacher"),
            teacher_name=data.get("teacher_name") or data.get("staff_name") or data.get("employee_name"),
            course=data.get("course"),
            semester=data.get("semester"),
            section=data.get("section"),
            day_value=data.get("day_value"),
            short_name=data.get("short_name"),
            degree_name=data.get("degree_name"),
            course_name=data.get("course_name")
        )


@dataclass(slots=True)
class DayOrderRecord:
    day_order_date: str
    day_order_value: int
    day_order_text: str
    timetable: List[DayOrderTimetableItem]

    @classmethod
    def from_dict(cls, data):
        return cls(
            day_order_date=data.get("day_order_date"),
            day_order_value=data.get("day_order_value"),
            day_order_text=data.get("day_order_text"),
            timetable=[
                DayOrderTimetableItem.from_dict(item)
                for item in data.get("timetable", [])
            ]
        )


@dataclass(slots=True)
class FullAttendance:
    status: str
    message: str
    student_course: dict
    semester_start_date: str
    semester_end_date: str
    dayorder_records: List[DayOrderRecord]
    attendance_records: List[FullAttendanceRecord]

    @classmethod
    def from_dict(cls, data):
        status = data.get("status", "0")
        message = data.get("message", "")
        raw_data = data.get("data", {})
        
        student_course = raw_data.get("student_course", {})
        semester = raw_data.get("semester", {})
        
        dayorder_records = [
            DayOrderRecord.from_dict(item)
            for item in raw_data.get("dayorder_records", [])
        ]
        
        attendance_records = [
            FullAttendanceRecord.from_dict(item)
            for item in raw_data.get("attendance_data", [])
        ]

        return cls(
            status=status,
            message=message,
            student_course=student_course,
            semester_start_date=semester.get("start_date"),
            semester_end_date=semester.get("end_date"),
            dayorder_records=dayorder_records,
            attendance_records=attendance_records
        )


@dataclass(slots=True)
class SubjectAttendance:
    id: int
    subject_id: int
    subject_code: str
    subject_name: str
    total_hours: int
    total_hours_present: int
    total_hours_absent: float
    total_percentage: float
    short_name: Optional[str] = None
    last_updated_on: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        try:
            absent = float(data.get("total_hours_absent", 0))
        except ValueError:
            absent = 0.0

        return cls(
            id=data.get("id"),
            subject_id=data.get("subject_id"),
            subject_code=data.get("subject_code"),
            subject_name=data.get("subject_name"),
            total_hours=data.get("total_hours", 0),
            total_hours_present=data.get("total_hours_present", 0),
            total_hours_absent=absent,
            total_percentage=float(data.get("total_percentage", 0.0)),
            short_name=data.get("short_name"),
            last_updated_on=data.get("last_updated_on")
        )