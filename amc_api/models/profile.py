from dataclasses import dataclass


@dataclass(slots=True)
class Profile:

    id: int
    uuid: str
    student_name: str
    register_no: str
    email: str
    mobile: str
    semester: int
    course_name: str
    department_name: str
    batch: str
    college_year: str

    @classmethod
    def from_dict(cls, data):

        return cls(
            id=data["id"],
            uuid=data["uuid"],
            student_name=data["student_name"].strip(),
            register_no=data["registerno"],
            email=data["email"],
            mobile=data["mobile"],
            semester=data["semester"],
            course_name=data["course_name"],
            department_name=data["department_name"],
            batch=data["batch"],
            college_year=data["college_year"],
        )

    def __str__(self):

        return (
            f"{self.student_name} "
            f"({self.register_no})"
        )

