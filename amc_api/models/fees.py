from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class FeesDetail:

    fee_type: str
    amount: str
    paid: str
    balance: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            fee_type=data.get("fee_type_name", ""),
            amount=data.get("amount", "0.00"),
            paid=data.get("paid_amount", "0.00"),
            balance=data.get("balance_amount", "0.00")
        )


@dataclass(slots=True)
class Fees:

    balance: str
    details: List[FeesDetail]

    @classmethod
    def from_dict(cls, data):
        return cls(
            balance=data.get("balance", "0.00"),
            details=[
                FeesDetail.from_dict(item)
                for item in data.get("data", [])
            ]
        )