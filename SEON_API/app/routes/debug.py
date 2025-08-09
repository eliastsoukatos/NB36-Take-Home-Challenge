from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from ..services.store import get_webhook_attempts
from ..utils.errors import success_envelope

router = APIRouter()


@router.get("/__debug/webhook-attempts")
async def debug_webhook_attempts(limit: Optional[int] = Query(default=50, ge=0, le=1000)):
    """
    Returns the last N webhook attempts recorded by the emitter.
    Query: limit (default 50, max 1000)
    """
    attempts = get_webhook_attempts(limit=limit)
    return success_envelope(attempts)
