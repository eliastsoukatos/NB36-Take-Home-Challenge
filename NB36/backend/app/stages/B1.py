import time
import uuid
from typing import Any, Dict, Optional, List

# In-memory case store for demo purposes
_CASES: Dict[str, Dict[str, Any]] = {}


def create_case(intake: Dict[str, Any]) -> Dict[str, Any]:
    case_id = str(uuid.uuid4())
    now = int(time.time())
    intake_sanitized = {k: (v.strip() if isinstance(v, str) else v) for k, v in intake.items()}

    case = {
        "case_id": case_id,
        "created_at": now,
        "status": "CREATED",
        "intake": intake_sanitized,
        "timeline": [{"ts": now, "event": "case.created"}],
    }
    _CASES[case_id] = case
    return case


def get_case(case_id: str) -> Optional[Dict[str, Any]]:
    return _CASES.get(case_id)


def update_case(case_id: str, **updates: Any) -> None:
    if case_id in _CASES:
        _CASES[case_id].update(updates)


def append_timeline(case_id: str, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
    if case_id in _CASES:
        entry: Dict[str, Any] = {"ts": int(time.time()), "event": event}
        if payload is not None:
            entry["payload"] = payload
        timeline: List[Dict[str, Any]] = _CASES[case_id].setdefault("timeline", [])
        timeline.append(entry)
