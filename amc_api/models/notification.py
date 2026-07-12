from dataclasses import dataclass
from typing import Optional, Any


@dataclass(slots=True)
class NotificationCount:

    count: int
    library_data: Optional[Any]

    @classmethod
    def from_dict(cls, data):
        count_val = 0
        raw_data = data.get("data")
        if isinstance(raw_data, list) and len(raw_data) > 0:
            count_val = raw_data[0].get("count", 0)
        elif isinstance(raw_data, dict):
            count_val = raw_data.get("count", 0)

        return cls(
            count=count_val,
            library_data=data.get("librarydata")
        )

    def __str__(self):
        return f"Notifications: {self.count}"