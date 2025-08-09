from __future__ import annotations

from fastapi import Header, HTTPException


async def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-KEY")) -> None:
    """
    Dependency to enforce X-API-KEY authentication across protected endpoints.
    - Missing key -> 401 with detail "AUTH_MISSING_KEY"
    - Invalid key -> 401 with detail "AUTH_INVALID_KEY"
    The error handler maps these to SEON-like error envelopes.
    """
    # Local import to avoid circulars at import time
    from ..config import settings

    if x_api_key is None or x_api_key == "":
        raise HTTPException(status_code=401, detail="AUTH_MISSING_KEY")
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="AUTH_INVALID_KEY")
    # success: return None
    return None
