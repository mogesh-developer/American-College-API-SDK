from dataclasses import dataclass
from typing import List, Optional


@dataclass(slots=True)
class Holiday:

    id: int
    holiday_date: str
    holiday_name: str
    holiday_type: str
    day_type: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            holiday_date=data.get("holiday_date"),
            holiday_name=data.get("holiday_name"),
            holiday_type=data.get("holiday_type"),
            day_type=data.get("day_type")
        )


@dataclass(slots=True)
class TimetableItem:

    hour: int
    subject_id: Optional[int]
    subject_name: Optional[str]
    teacher_name: Optional[str]

    @classmethod
    def from_dict(cls, data):
        return cls(
            hour=data.get("hour_value") or data.get("hour", 0),
            subject_id=data.get("subject_id") or data.get("subject"),
            subject_name=data.get("subject_name"),
            teacher_name=data.get("teacher_name") or data.get("employee_name") or data.get("staff_name")
        )


@dataclass(slots=True)
class Timetable:

    status: str
    message: str
    is_holiday: bool
    holiday: Optional[Holiday] = None
    schedule: Optional[List[TimetableItem]] = None

    @classmethod
    def from_dict(cls, data):
        status = data.get("status", "0")
        message = data.get("message", "")
        raw_data = data.get("data")
        is_holiday = False
        holiday = None
        schedule = None

        if isinstance(raw_data, dict) and "holiday_name" in raw_data:
            is_holiday = True
            holiday = Holiday.from_dict(raw_data)
        elif isinstance(raw_data, list):
            schedule = [
                TimetableItem.from_dict(item)
                for item in raw_data
            ]
        elif isinstance(raw_data, dict):
            schedule = [TimetableItem.from_dict(raw_data)]

        return cls(
            status=status,
            message=message,
            is_holiday=is_holiday,
            holiday=holiday,
            schedule=schedule
        )
