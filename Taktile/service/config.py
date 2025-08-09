import os
from pydantic import BaseModel


class Settings(BaseModel):
    # SEON mock service configuration (the external system "S")
    SEON_BASE_URL: str = os.getenv("SEON_BASE_URL", "http://localhost:8081")
    API_KEY_SEON: str = os.getenv("API_KEY_SEON", "secret")

    # Experian mock (Credit Profile) configuration
    EXPERIAN_BASE_URL: str = os.getenv("EXPERIAN_BASE_URL", "http://localhost:8000")
    EXPERIAN_TOKEN: str = os.getenv("EXPERIAN_TOKEN", "sandbox-token")
    EXPERIAN_CLIENT_REF: str = os.getenv("EXPERIAN_CLIENT_REF", "SBMYSQL")
    EXPERIAN_TIMEOUT_SECONDS: float = float(os.getenv("EXPERIAN_TIMEOUT_SECONDS", "8.0"))


settings = Settings()
