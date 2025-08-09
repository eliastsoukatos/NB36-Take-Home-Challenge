import hashlib
import json
import logging
import random
import time
import uuid
from typing import Any, Dict, Optional, Tuple

from fastapi import Request

logger = logging.getLogger("plaid_api")


def gen_request_id() -> str:
    return str(uuid.uuid4())


def stable_seed(key: str) -> int:
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def rng_from_key(key: str) -> random.Random:
    return random.Random(stable_seed(key))


def plaid_error(error_type: str, error_code: str, message: str, request_id: Optional[str] = None) -> Dict[str, Any]:
    return {
        "error_type": error_type,
        "error_code": error_code,
        "display_message": message,
        "request_id": request_id or gen_request_id(),
    }


def extract_options(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Options may come at top-level or nested under "options"
    opts = {}
    if isinstance(payload, dict):
        if isinstance(payload.get("options"), dict):
            opts.update(payload["options"])
        for k in ("force_mode", "coverage_months", "risk_profile", "inject_error"):
            if k in payload and k not in opts:
                opts[k] = payload[k]
    return opts


async def get_body_json(request: Request) -> Dict[str, Any]:
    try:
        # Request body may be consumed once; use receive buffering if needed
        body = await request.body()
        if not body:
            return {}
        return json.loads(body.decode("utf-8"))
    except Exception:
        return {}


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
