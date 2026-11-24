from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(slots=True)
class ElectiveSubject:
    id: Optional[Any]
    subject_code: str
    subject_name: str
    elective_type: Optional[str] = None
    credits: Optional[Any] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            id=data.get("id") or data.get("elective_id"),
            subject_code=str(data.get("subject_code") or data.get("sub_code") or ""),
            subject_name=str(data.get("subject_name") or data.get("sub_name") or ""),
            elective_type=data.get("elective_type") or data.get("type"),
            credits=data.get("credits"),
            raw_data=data
        )

