from dataclasses import dataclass
from typing import Optional
from .timetable import Holiday


@dataclass(slots=True)
class DayValue:

    status: str
    message: str
    is_holiday: bool
    holiday: Optional[Holiday] = None
    day_order_value: Optional[int] = None
    day_order_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        status = data.get("status", "0")
        message = data.get("message", "")
        raw_data = data.get("data")
        is_holiday = False
        holiday = None
        day_order_value = None
        day_order_text = None

        if isinstance(raw_data, dict):
            if "holiday_name" in raw_data:
                is_holiday = True
                holiday = Holiday.from_dict(raw_data)
            else:
                day_order_value = raw_data.get("day_order_value")
                day_order_text = raw_data.get("day_order_text")

        return cls(
            status=status,
            message=message,
            is_holiday=is_holiday,
            holiday=holiday,
            day_order_value=day_order_value,
            day_order_text=day_order_text
        )

    def __str__(self):
        if self.is_holiday and self.holiday:
            return f"Holiday: {self.holiday.holiday_name} ({self.holiday.holiday_date})"
        return f"Day Order: {self.day_order_text} (value={self.day_order_value})"
