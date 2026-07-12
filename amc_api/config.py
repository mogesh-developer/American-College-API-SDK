import os
from dataclasses import dataclass


@dataclass(slots=True)
class Config:

    base_url: str = os.getenv("AMC_BASE_URL", "https://portal.americancollege.edu.in")

    timeout: int = int(os.getenv("AMC_TIMEOUT", "30"))

    verify_ssl: bool = os.getenv("AMC_VERIFY_SSL", "True").lower() in ("true", "1", "yes")

    user_agent: str = os.getenv("AMC_USER_AGENT", "amc-api/0.1.0")

    enable_logging: bool = os.getenv("AMC_ENABLE_LOGGING", "False").lower() in ("true", "1", "yes")
