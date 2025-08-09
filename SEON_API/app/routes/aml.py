from __future__ import annotations

import hashlib
from fastapi import APIRouter, Request

from ..models import AMLRequest
from ..services.generators import build_aml_data, derive_scenario
from ..services.webhooks import maybe_emit_status_update
from ..utils.errors import success_envelope

router = APIRouter()


@router.post("/SeonRestService/aml-api/v1")
async def aml_v1(payload: AMLRequest, request: Request):
    """
    Mimic SEON AML API v1.
    - Requires X-API-KEY via global dependency (attached in main.py)
    - Scenario driven by custom_fields.scenario or email domain heuristic
    - Returns minimal but realistic AML matching booleans and payloads
    """
    data = build_aml_data(payload)

    # Optionally emit webhook if configured and requested
    try:
        scenario = derive_scenario(payload.email, payload.custom_fields)
        state = {"pass": "APPROVE", "review": "REVIEW", "ko_fraud": "APPROVE", "ko_compliance": "DECLINE"}[scenario.value]
        raw = f"{payload.user_fullname}|{payload.user_dob}|{payload.user_country}|{payload.email}"
        txn_id = "aml_" + hashlib.sha256((raw or "").encode("utf-8")).hexdigest()[:16]
        await maybe_emit_status_update(payload.custom_fields, txn_id, state, getattr(request.state, "request_id", None))
    except Exception:
        # Do not fail request due to webhook issues
        pass

    return success_envelope(data.model_dump())
