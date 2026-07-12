from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class FeeServiceGroupItem:

    id: int
    name: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            name=data.get("service_group_name") or data.get("name") or ""
        )


@dataclass(slots=True)
class FeeServiceGroupsResponse:

    status: str
    message: str
    groups: List[FeeServiceGroupItem]

    @classmethod
    def from_dict(cls, data):
        status = data.get("status", "0")
        message = data.get("message", "")
        raw_data = data.get("data")
        groups = []

        if isinstance(raw_data, list):
            groups = [
                FeeServiceGroupItem.from_dict(item)
                for item in raw_data
            ]
        elif isinstance(raw_data, dict):
            groups = [FeeServiceGroupItem.from_dict(raw_data)]

        return cls(
            status=status,
            message=message,
            groups=groups
        )
