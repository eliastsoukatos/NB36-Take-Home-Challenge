import os
from pydantic import BaseModel


class Settings(BaseModel):
    # SEON mock service configuration (the external system "S")
    SEON_BASE_URL: str = os.getenv("SEON_BASE_URL", "http://localhost:8081")
    API_KEY_SEON: str = os.getenv("API_KEY_SEON", "secret")


settings = Settings()
