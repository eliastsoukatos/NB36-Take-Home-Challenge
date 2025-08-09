from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional

import httpx

from ..config import settings
from .store import WebhookAttempt, get_label, record_webhook_attempt


EVENT_TYPE_STATUS = "transaction:status_update"


def _now_utc_iso() -> str:
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()


def _sign_hmac(body: bytes) -> str:
    key = (settings.secret_key or "").encode("utf-8")
    digest = hmac.new(key, body, hashlib.sha256).hexdigest()
    return f"SHA-256={digest}"


async def _post(url: str, event_type: str, payload: Dict[str, Any], request_id: Optional[str]) -> None:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Digest": _sign_hmac(body),
        "X-Event-Type": event_type,
    }
    if request_id:
        headers["X-Request-ID"] = request_id

    start = time.perf_counter()
    attempt: WebhookAttempt = {
        "ts": _now_utc_iso(),
        "url": url,
        "event_type": event_type,
        "payload": payload,  # stored for debug only
        "headers": {"Digest": headers["Digest"], "X-Event-Type": event_type, **({"X-Request-ID": request_id} if request_id else {})},
        "status_code": None,
        "ok": False,
        "duration_ms": 0,
        "error": None,
        "request_id": request_id,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
            resp = await client.post(url, content=body, headers=headers)
            attempt["status_code"] = resp.status_code
            attempt["ok"] = bool(resp.is_success)
    except Exception as e:
        attempt["error"] = str(e)
    finally:
        attempt["duration_ms"] = int((time.perf_counter() - start) * 1000)
        record_webhook_attempt(attempt)


async def emit_transaction_status_update(transaction_id: str, state: str, request_id: Optional[str]) -> None:
    """
    Emit a transaction status update webhook with HMAC signature if WEBHOOK_URL is configured.
    Body: { id, state, label? }
    Header: Digest: SHA-256=<hex>
    """
    if not settings.webhook_url:
        return
    payload: Dict[str, Any] = {"id": transaction_id, "state": state}
    label = get_label(transaction_id)
    if label:
        payload["label"] = label

    await _post(settings.webhook_url, EVENT_TYPE_STATUS, payload, request_id)


async def maybe_emit_status_update(custom_fields: Optional[Dict[str, Any]], transaction_id: str, state: str, request_id: Optional[str]) -> None:
    """
    Conditionally emit status update webhook if:
    - WEBHOOK_URL is set, and
    - custom_fields.emit_webhooks is true
    """
    if not settings.webhook_url:
        return
    emit = False
    if custom_fields and isinstance(custom_fields, dict):
        emit = bool(custom_fields.get("emit_webhooks"))
    if not emit:
        return
    await emit_transaction_status_update(transaction_id, state, request_id)
