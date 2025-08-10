from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseModel, Field


class Settings(BaseModel):
    # Core env config
    api_key: str = Field(default_factory=lambda: os.getenv("API_KEY", "secret"))
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "devsecret"))
    webhook_url: Optional[str] = Field(default_factory=lambda: os.getenv("WEBHOOK_URL"))

    # Server config
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8080")))
    env: str = Field(default_factory=lambda: os.getenv("ENV", "dev"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # CORS
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["*"]
    )

    # Webhook
    webhook_timeout_seconds: float = Field(default=5.0)
    webhook_debug_buffer: int = Field(default=50)

    model_config = {
        "frozen": True,
        "str_strip_whitespace": True,
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
