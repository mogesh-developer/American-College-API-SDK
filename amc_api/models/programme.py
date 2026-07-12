from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class ProgrammeItem:

    stco_id: int
    course_id: int
    course_name: str
    course_short_name: str
    degree_name: str
    course_type: str
    batch: str
    semester: int
    section: str
    admission_no: str
    register_no: str
    roll_no: str
    admission_date: str
    programme_type: str
    stco_row_type: str
    is_primary: int

    @classmethod
    def from_dict(cls, data):
        return cls(
            stco_id=data.get("stco_id"),
            course_id=data.get("course_id"),
            course_name=data.get("course_name"),
            course_short_name=data.get("course_short_name"),
            degree_name=data.get("degree_name"),
            course_type=data.get("course_type"),
            batch=data.get("batch"),
            semester=data.get("semester"),
            section=data.get("section"),
            admission_no=data.get("admission_no"),
            register_no=data.get("register_no"),
            roll_no=data.get("roll_no"),
            admission_date=data.get("admission_date"),
            programme_type=data.get("programme_type"),
            stco_row_type=data.get("stco_row_type"),
            is_primary=data.get("is_primary")
        )


@dataclass(slots=True)
class EnrolledProgrammes:

    status: str
    message: str
    show_programme_list: bool
    programmes: List[ProgrammeItem]

    @classmethod
    def from_dict(cls, data):
        return cls(
            status=data.get("status", "0"),
            message=data.get("message", ""),
            show_programme_list=data.get("show_programme_list", False),
            programmes=[
                ProgrammeItem.from_dict(item)
                for item in data.get("programmes", [])
            ]
        )
