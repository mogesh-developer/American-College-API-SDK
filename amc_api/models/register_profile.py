from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class RegisterProfile:

    id: int
    uuid: str
    name: str
    register_no: str
    admission_no: str
    admission_date: str
    batch: str
    academic_year: str
    gender: str
    dob: str
    mobile: str
    email: str
    personal_email: str
    father_name: str
    father_phone: str
    mother_phone: Optional[str]
    father_occupation: Optional[str]
    annual_income: Optional[int]
    street_permanent: Optional[str]
    caste: Optional[str]
    community_name: Optional[str]

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            uuid=data.get("uuid"),
            name=data.get("name"),
            register_no=data.get("registerno"),
            admission_no=data.get("admissionno"),
            admission_date=data.get("admissiondate"),
            batch=data.get("batch"),
            academic_year=data.get("acyear") or data.get("academicyear"),
            gender=data.get("gender"),
            dob=data.get("dob"),
            mobile=data.get("mobile"),
            email=data.get("email"),
            personal_email=data.get("personal_email"),
            father_name=data.get("fathername"),
            father_phone=data.get("fatherphone"),
            mother_phone=data.get("motherphone"),
            father_occupation=data.get("fatheroccupation"),
            annual_income=data.get("annualincome"),
            street_permanent=data.get("street_permanent"),
            caste=data.get("caste"),
            community_name=data.get("community_name")
        )

    def __str__(self):
        return f"{self.name} ({self.register_no}) - Registration Profile"
