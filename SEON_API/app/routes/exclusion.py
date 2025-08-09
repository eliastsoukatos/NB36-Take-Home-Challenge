from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import ExclusionIn
from ..services.store import add_exclusions, remove_exclusions, snapshot_exclusions
from ..utils.errors import success_envelope

router = APIRouter()


@router.put("/SeonRestService/fraud-api/exclude/v1")
async def put_exclusions(payload: ExclusionIn):
    """
    Add self-exclusion entries.
    Body: { user_ids?: [str], emails?: [str] }
    Returns counts of created rules.
    """
    if not payload.user_ids and not payload.emails:
        raise HTTPException(status_code=400, detail="At least one of user_ids or emails must be provided")

    summary = add_exclusions(payload)
    return success_envelope(summary)


@router.delete("/SeonRestService/fraud-api/exclude/v1")
async def delete_exclusions(payload: ExclusionIn):
    """
    Remove self-exclusion entries.
    Body: { user_ids?: [str], emails?: [str] }
    Returns counts of deleted rules.
    """
    if not payload.user_ids and not payload.emails:
        raise HTTPException(status_code=400, detail="At least one of user_ids or emails must be provided")

    summary = remove_exclusions(payload)
    return success_envelope(summary)


@router.get("/SeonRestService/fraud-api/exclude/v1")
async def get_exclusions_snapshot():
    """
    Returns a snapshot of current self-exclusions for debugging.
    """
    snap = snapshot_exclusions()
    return success_envelope(snap)
