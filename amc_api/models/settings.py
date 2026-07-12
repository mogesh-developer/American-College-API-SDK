import base64
import json
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(slots=True)
class Settings:

    raw: str
    fields: Dict[str, str]

    @classmethod
    def from_dict(cls, data):
        raw_jwt = data.get("data", "")
        fields = {}

        try:
            parts = raw_jwt.split(".")
            if len(parts) >= 2:
                payload_b64 = parts[1]
                payload_b64 += "=" * (4 - len(payload_b64) % 4)
                payload_bytes = base64.b64decode(payload_b64)
                decoded_list = json.loads(payload_bytes.decode("utf-8"))
                for item in decoded_list:
                    name = item.get("field_name")
                    value = item.get("field_value")
                    if name:
                        fields[name] = value
        except Exception:
            pass

        return cls(
            raw=raw_jwt,
            fields=fields
        )

    def get(self, key: str, default: Any = None) -> Any:
        return self.fields.get(key, default)

    def __getattr__(self, name: str) -> Any:
        if name in self.fields:
            return self.fields[name]
        raise AttributeError(f"'Settings' object has no attribute '{name}'")
