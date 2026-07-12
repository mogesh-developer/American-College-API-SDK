from dataclasses import dataclass


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