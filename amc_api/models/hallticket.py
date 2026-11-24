from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass(slots=True)
class HallTicketSubject:
    subject_code: str
    subject_name: str
    exam_date: Optional[str] = None
    session: Optional[str] = None
    seat_no: Optional[str] = None
    hall_name: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            subject_code=str(data.get("subject_code") or data.get("sub_code") or ""),
            subject_name=str(data.get("subject_name") or data.get("sub_name") or ""),
            exam_date=data.get("exam_date") or data.get("date"),
            session=data.get("session") or data.get("exam_session"),
            seat_no=data.get("seat_no") or data.get("seat"),
            hall_name=data.get("hall_name") or data.get("hall"),
            raw_data=data
        )


@dataclass(slots=True)
class HallTicket:
    exam_name: Optional[str]
    register_no: Optional[str]
    student_name: Optional[str]
    subjects: List[HallTicketSubject]
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        sub_list = data.get("subjects") or data.get("data") or []
        if isinstance(sub_list, dict):
            sub_list = sub_list.get("subject_list") or []
        elif not isinstance(sub_list, list):
            sub_list = []

        return cls(
            exam_name=data.get("exam_name") or data.get("examination"),
            register_no=data.get("registerno") or data.get("register_no"),
            student_name=data.get("student_name") or data.get("name"),
            subjects=[HallTicketSubject.from_dict(s) for s in sub_list if isinstance(s, dict)],
            raw_data=data
        )

