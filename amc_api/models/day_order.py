from dataclasses import dataclass


@dataclass(slots=True)
class DayOrder:

    id: int
    created_on: str
    company_id: int
    day_order_date: str
    day_order_value: int
    day_order_text: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            created_on=data.get("created_on"),
            company_id=data.get("company_id"),
            day_order_date=data.get("day_order_date"),
            day_order_value=data.get("day_order_value"),
            day_order_text=data.get("day_order_text")
        )

    def __str__(self):
        return f"Day Order {self.day_order_text} on {self.day_order_date}"
