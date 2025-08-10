from pydantic import BaseModel
import os


class Settings(BaseModel):
    # Taktile service base URL (the orchestrator we call from backend)
    TAKTILE_BASE_URL: str = os.getenv("TAKTILE_BASE_URL", "http://localhost:9100")
    #TAKTILE_BASE_URL: str = os.getenv("TAKTILE_BASE_URL", "https://nb-taktile.onrender.com")

settings = Settings()
