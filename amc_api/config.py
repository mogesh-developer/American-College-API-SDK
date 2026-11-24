import os
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Config:

    base_url: str = field(
        default_factory=lambda: os.getenv("AMC_BASE_URL", "https://portal.americancollege.edu.in").rstrip("/")
    )

    timeout: int = field(
        default_factory=lambda: int(os.getenv("AMC_TIMEOUT", "30"))
    )

    verify_ssl: bool = field(
        default_factory=lambda: os.getenv("AMC_VERIFY_SSL", "True").lower() in ("true", "1", "yes")
    )

    user_agent: str = field(
        default_factory=lambda: os.getenv("AMC_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    )

    enable_logging: bool = field(
        default_factory=lambda: os.getenv("AMC_ENABLE_LOGGING", "False").lower() in ("true", "1", "yes")
    )

    custom_endpoints: Dict[str, str] = field(default_factory=dict)

    def get_endpoint(self, key: str, default: str) -> str:
        """Resolve endpoint dynamically allowing environment variable or runtime overrides."""
        env_key = f"AMC_ENDPOINT_{key.upper()}"
        return os.getenv(env_key, self.custom_endpoints.get(key, default))

