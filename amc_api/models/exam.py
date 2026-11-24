from dataclasses import dataclass
from typing import Optional, Any, Dict, List


@dataclass(slots=True)
class InternalMark:
    subject_code: str
    subject_name: str
    mark: Optional[str] = None
    max_mark: Optional[str] = None
    test_name: Optional[str] = None
    semester: Optional[Any] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            subject_code=str(data.get("subject_code") or data.get("sub_code") or ""),
            subject_name=str(data.get("subject_name") or data.get("sub_name") or ""),
            mark=str(data.get("mark") or data.get("secured_mark") or data.get("marks") or ""),
            max_mark=str(data.get("max_mark") or data.get("maximum_mark") or ""),
            test_name=data.get("test_name") or data.get("exam_name"),
            semester=data.get("semester") or data.get("sem"),
            raw_data=data
        )


@dataclass(slots=True)
class ExamResultItem:
    subject_code: str
    subject_name: str
    grade: Optional[str] = None
    result: Optional[str] = None
    credits: Optional[Any] = None
    internal_mark: Optional[str] = None
    external_mark: Optional[str] = None
    total_mark: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            subject_code=str(data.get("subject_code") or data.get("sub_code") or ""),
            subject_name=str(data.get("subject_name") or data.get("sub_name") or ""),
            grade=data.get("grade") or data.get("letter_grade"),
            result=data.get("result") or data.get("pass_fail"),
            credits=data.get("credits") or data.get("credit"),
            internal_mark=str(data.get("int_mark") or data.get("internal") or ""),
            external_mark=str(data.get("ext_mark") or data.get("external") or ""),
            total_mark=str(data.get("total") or data.get("total_mark") or ""),
            raw_data=data
        )


@dataclass(slots=True)
class ExamResult:
    exam_month: Optional[str] = None
    gpa: Optional[str] = None
    cgpa: Optional[str] = None
    items: List[ExamResultItem] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        results_raw = data.get("data") or data.get("results") or []
        if isinstance(results_raw, dict):
            items_list = results_raw.get("marks") or results_raw.get("subjects") or []
        elif isinstance(results_raw, list):
            items_list = results_raw
        else:
            items_list = []

        items = [ExamResultItem.from_dict(item) for item in items_list if isinstance(item, dict)]
        return cls(
            exam_month=data.get("exam_month") or data.get("month"),
            gpa=str(data.get("gpa") or ""),
            cgpa=str(data.get("cgpa") or ""),
            items=items,
            raw_data=data
        )

