from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import ListEntryIn
from ..services.store import get_list_entries, set_list_entry
from ..utils.errors import success_envelope

router = APIRouter()

_ALLOWED_STATES = {"blacklist", "whitelist", "normal"}


@router.put("/SeonRestService/fraud-api/state-field/v1/")
async def put_state_field(entry: ListEntryIn):
    """
    Stores a state entry for a given data_field and value.
    Body: { data_field, value, state, comment?, expire_day? }
    Returns the created/updated record.
    """
    if entry.state not in _ALLOWED_STATES:
        raise HTTPException(status_code=400, detail=f"Invalid state '{entry.state}'. Allowed: {sorted(_ALLOWED_STATES)}")

    out = set_list_entry(entry)
    return success_envelope(out.model_dump())


@router.get("/SeonRestService/fraud-api/state-field/v1/entries")
async def list_state_entries():
    """
    Returns current (non-expired) list entries for debugging/inspection.
    """
    items = get_list_entries()
    return success_envelope([i.model_dump() for i in items])
