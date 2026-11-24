from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(slots=True)
class PlacementJob:
    id: Optional[Any]
    company_name: str
    job_title: str
    salary_package: Optional[str] = None
    last_date: Optional[str] = None
    description: Optional[str] = None
    eligibility: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            id=data.get("id") or data.get("job_id"),
            company_name=str(data.get("company_name") or data.get("company") or ""),
            job_title=str(data.get("job_title") or data.get("designation") or data.get("title") or ""),
            salary_package=data.get("salary_package") or data.get("ctc") or data.get("salary"),
            last_date=data.get("last_date") or data.get("deadline"),
            description=data.get("description") or data.get("job_description"),
            eligibility=data.get("eligibility") or data.get("criteria"),
            raw_data=data
        )

