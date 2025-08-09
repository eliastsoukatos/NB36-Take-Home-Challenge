from __future__ import annotations

import datetime as dt
from collections import deque
from threading import Lock
from typing import Deque, Dict, List, Optional, Set, Tuple, TypedDict

from ..config import settings
from ..models import ExclusionIn, LabelItem, ListEntryIn, ListEntryOut


# ------------- In-memory stores (module-level singletons) -------------

_lists_lock = Lock()
_labels_lock = Lock()
_exclusions_lock = Lock()
_webhook_lock = Lock()

# (data_field, value) -> record
_lists: Dict[Tuple[str, str], Dict[str, Optional[str]]] = {}

# transaction_id -> label
_labels: Dict[str, str] = {}

# exclusions
_exclusion_user_ids: Set[str] = set()
_exclusion_emails: Set[str] = set()

# webhook attempts circular buffer
class WebhookAttempt(TypedDict, total=False):
    ts: str
    url: str
    event_type: str
    payload: Dict
    headers: Dict[str, str]
    status_code: Optional[int]
    ok: bool
    duration_ms: int
    error: Optional[str]
    request_id: Optional[str]


_webhook_attempts: Deque[WebhookAttempt] = deque(maxlen=settings.webhook_debug_buffer)


# ------------- Helpers -------------

def _now_utc_iso() -> str:
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()


def _iso_in_days(days: int) -> str:
    return (dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) + dt.timedelta(days=days)).isoformat()


def _is_expired(iso_when: Optional[str]) -> bool:
    if not iso_when:
        return False
    try:
        when = dt.datetime.fromisoformat(iso_when)
    except Exception:
        return False
    now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
    return when <= now


def prune_expired_list_entries() -> None:
    with _lists_lock:
        expired_keys: List[Tuple[str, str]] = []
        for key, rec in _lists.items():
            if _is_expired(rec.get("expire_at")):
                expired_keys.append(key)
        for key in expired_keys:
            _lists.pop(key, None)


# ------------- Lists API operations -------------

def set_list_entry(entry: ListEntryIn) -> ListEntryOut:
    created_at = _now_utc_iso()
    expire_at = _iso_in_days(entry.expire_day) if entry.expire_day else None
    record = {
        "state": entry.state,
        "comment": entry.comment,
        "created_at": created_at,
        "expire_at": expire_at,
    }
    key = (entry.data_field, entry.value)
    with _lists_lock:
        _lists[key] = record

    return ListEntryOut(
        data_field=entry.data_field,
        value=entry.value,
        state=entry.state,
        comment=entry.comment,
        created_at=created_at,
        expire_at=expire_at,
    )


def get_list_entries() -> List[ListEntryOut]:
    prune_expired_list_entries()
    out: List[ListEntryOut] = []
    with _lists_lock:
        for (data_field, value), rec in _lists.items():
            out.append(
                ListEntryOut(
                    data_field=data_field,
                    value=value,
                    state=str(rec.get("state") or ""),
                    comment=rec.get("comment"),
                    created_at=str(rec.get("created_at") or _now_utc_iso()),
                    expire_at=rec.get("expire_at"),
                )
            )
    return out


# ------------- Labels API operations -------------

_ALLOWED_LABELS: Set[str] = {
    "fraud_confirmed",
    "fraud_suspected",
    "chargeback",
    "bnpl_default",
    "customer_complaint",
    "not_fraud",
}

def allowed_labels() -> Set[str]:
    return set(_ALLOWED_LABELS)


def set_labels(items: List[LabelItem]) -> Dict[str, object]:
    successes: List[str] = []
    invalids: List[Dict[str, str]] = []
    with _labels_lock:
        for item in items:
            if item.label not in _ALLOWED_LABELS:
                invalids.append({"transaction_id": item.transaction_id, "label": item.label})
                continue
            _labels[item.transaction_id] = item.label
            successes.append(item.transaction_id)
    return {"updated": successes, "invalid": invalids, "allowed_labels": sorted(_ALLOWED_LABELS)}


def get_label(transaction_id: str) -> Optional[str]:
    with _labels_lock:
        return _labels.get(transaction_id)


# ------------- Exclusion API operations -------------

def add_exclusions(payload: ExclusionIn) -> Dict[str, int]:
    added_users = 0
    added_emails = 0
    with _exclusions_lock:
        if payload.user_ids:
            for uid in payload.user_ids:
                if uid not in _exclusion_user_ids:
                    _exclusion_user_ids.add(uid)
                    added_users += 1
        if payload.emails:
            for email in payload.emails:
                if email not in _exclusion_emails:
                    _exclusion_emails.add(email)
                    added_emails += 1
    return {"user_ids_added": added_users, "emails_added": added_emails}


def remove_exclusions(payload: ExclusionIn) -> Dict[str, int]:
    removed_users = 0
    removed_emails = 0
    with _exclusions_lock:
        if payload.user_ids:
            for uid in payload.user_ids:
                if uid in _exclusion_user_ids:
                    _exclusion_user_ids.remove(uid)
                    removed_users += 1
        if payload.emails:
            for email in payload.emails:
                if email in _exclusion_emails:
                    _exclusion_emails.remove(email)
                    removed_emails += 1
    return {"user_ids_removed": removed_users, "emails_removed": removed_emails}


def snapshot_exclusions() -> Dict[str, List[str]]:
    with _exclusions_lock:
        return {
            "user_ids": sorted(_exclusion_user_ids),
            "emails": sorted(_exclusion_emails),
        }


# ------------- Webhook attempts -------------

def record_webhook_attempt(attempt: WebhookAttempt) -> None:
    with _webhook_lock:
        _webhook_attempts.append(attempt)


def get_webhook_attempts(limit: Optional[int] = None) -> List[WebhookAttempt]:
    with _webhook_lock:
        items = list(_webhook_attempts)
    if limit is not None and limit >= 0:
        return items[-limit:]
    return items
