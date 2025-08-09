from __future__ import annotations

from fastapi import APIRouter, Request

from ..models import FraudRequest
from ..services.generators import build_fraud_data
from ..services.webhooks import maybe_emit_status_update
from ..utils.errors import success_envelope

router = APIRouter()


@router.post("/SeonRestService/fraud-api/v2")
async def fraud_v2(payload: FraudRequest, request: Request):
    """
    Mimic SEON Fraud API v2.
    - Requires X-API-KEY via global dependency (attached in main.py)
    - Scenario driven by custom_fields.scenario or email domain heuristic
    - Optionally emits a signed webhook if WEBHOOK_URL set and custom_fields.emit_webhooks=true
    """
    data = build_fraud_data(payload)

    # Emit webhook if configured and requested
    try:
        await maybe_emit_status_update(payload.custom_fields, data.id, data.state, getattr(request.state, "request_id", None))
    except Exception:
        # Do not fail the main request due to webhook issues; debug attempts are recorded in the store.
        pass

    return success_envelope(data.model_dump())
