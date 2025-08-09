import os
from typing import Any, Dict, Optional, Tuple

from .utils import gen_request_id, plaid_error


EXPECTED_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
EXPECTED_SECRET = os.getenv("PLAID_SECRET")


def _extract_from_headers(headers: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    # FastAPI lower-cases header keys internally; accept both cases defensively
    cid = headers.get("PLAID-CLIENT-ID") or headers.get("plaid-client-id") or headers.get("x-plaid-client-id")
    sec = headers.get("PLAID-SECRET") or headers.get("plaid-secret") or headers.get("x-plaid-secret")
    return (cid, sec)


def _extract_from_body(body: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    cid = None
    sec = None
    if isinstance(body, dict):
        cid = body.get("client_id")
        sec = body.get("secret")
    return (cid, sec)


def validate_auth(headers: Dict[str, Any], body: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Returns (ok, error_json_or_empty). Always produce Plaid-style error body with HTTP 200 when not ok.
    Policy:
      - Accept credentials via headers or JSON body.
      - If EXPECTED_* envs are set, enforce equality.
      - Otherwise, allow any non-empty credentials for DX.
    """
    req_id = gen_request_id()

    h_cid, h_sec = _extract_from_headers(headers or {})
    b_cid, b_sec = _extract_from_body(body or {})

    client_id = h_cid or b_cid
    secret = h_sec or b_sec

    if not client_id or not secret:
        return False, plaid_error(
            error_type="INVALID_INPUT",
            error_code="INVALID_CREDENTIALS",
            message="Missing Plaid client_id/secret",
            request_id=req_id,
        )

    # Enforce expected if provided via env
    if EXPECTED_CLIENT_ID and client_id != EXPECTED_CLIENT_ID:
        return False, plaid_error(
            error_type="INVALID_INPUT",
            error_code="INVALID_CREDENTIALS",
            message="Invalid client_id",
            request_id=req_id,
        )
    if EXPECTED_SECRET and secret != EXPECTED_SECRET:
        return False, plaid_error(
            error_type="INVALID_INPUT",
            error_code="INVALID_CREDENTIALS",
            message="Invalid secret",
            request_id=req_id,
        )

    return True, {}
