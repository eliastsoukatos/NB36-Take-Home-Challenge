from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from ..models import LabelItem
from ..services.store import allowed_labels, set_labels
from ..utils.errors import success_envelope

router = APIRouter()


@router.put("/SeonRestService/fraud-api/transaction-label/v2")
async def put_transaction_labels(items: List[LabelItem]):
    """
    Accepts an array of { transaction_id, label } items.
    Validates label against a fixed set and stores them in-memory.
    Returns summary with updated IDs, invalids, and allowed_labels.
    """
    if not items:
        raise HTTPException(status_code=400, detail="No items provided")

    summary = set_labels(items)
    return success_envelope(summary)
