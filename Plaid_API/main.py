from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .auth import validate_auth
from .pdf import generate_bank_income_pdf
from .schemas import (
    AccessTokenRequest,
    BankIncome,
    BankIncomeRefreshResponse,
    BankIncomeResponse,
    CreditSessionMeta,
    CreditSessionsGetRequest,
    EmploymentRecord,
    EmploymentResponse,
    FireWebhookRequest,
    ItemPublicTokenExchangeRequest,
    ItemPublicTokenExchangeResponse,
    LinkTokenCreateRequest,
    LinkTokenCreateResponse,
    PayrollIncome,
    PayrollIncomeResponse,
    PayrollRiskSignalsResponse,
    RequestIdOnly,
    RiskSignal,
    UserCreateRequest,
    UserCreateResponse,
)
from .store import store
from .utils import extract_options, gen_request_id, now_iso, plaid_error, rng_from_key

app = FastAPI(title="Mock Plaid Income API", version="0.1.0")
logger = logging.getLogger("plaid_api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    rid = gen_request_id()
    request.state.request_id = rid
    logger.info("REQ %s %s rid=%s", request.method, request.url.path, rid)
    resp: Response = await call_next(request)
    # Best-effort header for correlating
    try:
        resp.headers["x-request-id"] = rid
    except Exception:
        pass
    return resp


# ----------------------------- helpers -----------------------------


def _inject_error_if_any(options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    code = (options.get("inject_error") or "").strip()
    if not code:
        return None
    # Map a few common Plaid errors (example codes)
    mapping = {
        "ITEM_LOGIN_REQUIRED": ("ITEM_ERROR", "ITEM_LOGIN_REQUIRED", "Item login required"),
        "RATE_LIMIT_EXCEEDED": ("RATE_LIMIT_EXCEEDED", "RATE_LIMIT_EXCEEDED", "Too many requests"),
        "INTERNAL_SERVER_ERROR": ("API_ERROR", "INTERNAL_SERVER_ERROR", "Internal error"),
    }
    etype, ecode, msg = mapping.get(code, ("INVALID_INPUT", "INVALID_REQUEST", f"Injected error: {code}"))
    return plaid_error(etype, ecode, msg)


def _require_item(req: AccessTokenRequest) -> Optional[Dict[str, Any]]:
    if not (req.access_token or req.client_user_id):
        return plaid_error("INVALID_INPUT", "INVALID_ACCESS_TOKEN", "Missing access_token or client_user_id")
    if req.access_token:
        item = store.resolve_item_by_access_token(req.access_token)
        if not item:
            return plaid_error("INVALID_INPUT", "INVALID_ACCESS_TOKEN", "Unknown access_token")
        return {"item": item, "client_user_id": item.client_user_id}
    # Fallback: allow direct usage with client_user_id for sandbox convenience
    return {"item": None, "client_user_id": req.client_user_id}  # type: ignore


def _derive_payroll_income(client_user_id: str, force_mode: Optional[str]) -> Optional[PayrollIncome]:
    if force_mode == "empty":
        return None
    if force_mode and force_mode not in ("payroll", "bank", "document", "empty"):
        force_mode = None

    rng = rng_from_key(f"payroll:{client_user_id}")
    employer = rng.choice(["Acme Corp", "Globex", "Initech", "Umbrella", "Soylent", "Stark Industries"])
    cadence = rng.choice(["WEEKLY", "BIWEEKLY", "SEMIMONTHLY", "MONTHLY"])
    base_gross = rng.uniform(1800, 3200)
    net = base_gross * rng.uniform(0.7, 0.82)
    ytd = round(base_gross * rng.randint(12, 26), 2)

    # If force_mode == "payroll", guarantee result present
    if force_mode in (None, "payroll"):
        return PayrollIncome(
            employer=employer,
            pay_frequency=cadence,  # type: ignore
            ytd_gross=round(ytd, 2),
            streams=[{"label": "Primary job", "cadence": cadence, "gross": round(base_gross, 2), "net": round(net, 2)}],  # type: ignore
        )
    # otherwise return empty to steer to next product
    return None


def _derive_bank_income(client_user_id: str, coverage_months: int, force_mode: Optional[str]) -> Optional[BankIncome]:
    if force_mode == "empty":
        return None

    rng = rng_from_key(f"bank:{client_user_id}")
    cadence = rng.choice(["WEEKLY", "BIWEEKLY", "SEMIMONTHLY", "MONTHLY"])
    avg_net = round(rng.uniform(1400, 2200), 2)
    conf = rng.choice(["LOW", "MEDIUM", "HIGH"])
    source = rng.choice(["Direct deposit", "Unknown", "Other"])

    coverage = "FULL" if coverage_months >= 12 else "PARTIAL"
    if force_mode == "bank" or force_mode is None:
        return BankIncome(coverage=coverage, streams=[{"source": source, "cadence": cadence, "average_net": avg_net, "confidence": conf}])  # type: ignore
    return None


def _derive_employment(client_user_id: str) -> EmploymentRecord:
    rng = rng_from_key(f"employment:{client_user_id}")
    employer = rng.choice(["Acme Corp", "Globex", "Initech", "Umbrella", "Soylent", "Stark Industries"])
    year = rng.randint(2017, 2023)
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    status = rng.choice(["ACTIVE", "INACTIVE"])
    return EmploymentRecord(employer=employer, status=status, hire_date=f"{year:04d}-{month:02d}-{day:02d}")


# ----------------------------- endpoints -----------------------------


@app.post("/user/create", response_model=UserCreateResponse)
async def user_create(request: Request, body: UserCreateRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        return err
    user_id = store.create_user(body.client_user_id)
    return {"user_id": user_id, "request_id": request.state.request_id}


@app.post("/link/token/create", response_model=LinkTokenCreateResponse)
async def link_token_create(request: Request, body: LinkTokenCreateRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        return err
    client_user_id = (body.user or {}).get("client_user_id")
    if not client_user_id:
        return plaid_error("INVALID_INPUT", "INVALID_REQUEST", "user.client_user_id required", request.state.request_id)
    store.create_user(client_user_id)
    link_token = store.create_link_token(client_user_id, {"webhook": body.webhook, "client_name": body.client_name})
    return {"link_token": link_token, "expiration": now_iso(), "request_id": request.state.request_id}


@app.post("/item/public_token/exchange", response_model=ItemPublicTokenExchangeResponse)
async def item_public_token_exchange(request: Request, body: ItemPublicTokenExchangeRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        return err
    client_user_id = body.client_user_id or "demo-user"
    store.create_user(client_user_id)
    out = store.create_item_from_public_token(body.public_token, client_user_id)
    return {"access_token": out["access_token"], "item_id": out["item_id"], "request_id": request.state.request_id}


@app.post("/credit/sessions/get", response_model=CreditSessionMeta)
async def credit_sessions_get(request: Request, body: CreditSessionsGetRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        return err
    rid = request.state.request_id
    opts = extract_options(body.model_dump())
    injected = _inject_error_if_any(opts)
    if injected:
        injected["request_id"] = rid
        return injected
    return {
        "session_id": body.session_id or f"sess-{rid[:8]}",
        "echo": (body.metadata or {}),
        "results": {"status": "ok", "force_mode": opts.get("force_mode")},
        "request_id": rid,
    }


@app.post("/credit/payroll_income/get", response_model=PayrollIncomeResponse)
async def payroll_income_get(request: Request, body: AccessTokenRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        return err
    rid = request.state.request_id
    opts = extract_options(body.model_dump())
    injected = _inject_error_if_any(opts)
    if injected:
        injected["request_id"] = rid
        return injected

    resolved = _require_item(body)
    if isinstance(resolved, dict) and "error_type" in resolved:
        resolved["request_id"] = rid
        return resolved
    client_user_id = resolved["client_user_id"]  # type: ignore

    pi = _derive_payroll_income(client_user_id, opts.get("force_mode"))
    return {"payroll_income": (pi.model_dump() if pi else None), "request_id": rid}


@app.post("/credit/payroll_income/risk_signals/get", response_model=PayrollRiskSignalsResponse)
async def payroll_risk_signals_get(request: Request, body: AccessTokenRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        return err
    rid = request.state.request_id
    opts = extract_options(body.model_dump())
    injected = _inject_error_if_any(opts)
    if injected:
        injected["request_id"] = rid
        return injected

    risk_profile = (opts.get("risk_profile") or "clean").lower()
    if risk_profile == "suspicious":
        signals = [
            {"code": "DOC_ALTERATION_SUSPECTED", "severity": "HIGH", "description": "Detected anomalies in uploaded doc."},
            {"code": "MISMATCH_EMPLOYER", "severity": "MEDIUM", "description": "Employer mismatch between sources."},
        ]
    else:
        signals = [
            {"code": "NO_FINDINGS", "severity": "LOW", "description": "No issues detected."},
        ]
    return {"signals": signals, "request_id": rid}


@app.post("/credit/bank_income/get", response_model=BankIncomeResponse)
async def bank_income_get(request: Request, body: AccessTokenRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        return err
    rid = request.state.request_id
    opts = extract_options(body.model_dump())
    injected = _inject_error_if_any(opts)
    if injected:
        injected["request_id"] = rid
        return injected

    resolved = _require_item(body)
    if isinstance(resolved, dict) and "error_type" in resolved:
        resolved["request_id"] = rid
        return resolved
    client_user_id = resolved["client_user_id"]  # type: ignore

    coverage_months = int(opts.get("coverage_months") or 12)
    bi = _derive_bank_income(client_user_id, coverage_months, opts.get("force_mode"))
    return {"bank_income": (bi.model_dump() if bi else None), "request_id": rid}


@app.post("/credit/bank_income/pdf/get")
async def bank_income_pdf_get(request: Request, body: AccessTokenRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        # Even errors for PDF requests are returned as JSON/plain 200; but PDF endpoint should return PDF normally.
        # Here, fall back to JSON error.
        return err
    rid = request.state.request_id
    opts = extract_options(body.model_dump())

    resolved = _require_item(body)
    if isinstance(resolved, dict) and "error_type" in resolved:
        resolved["request_id"] = rid
        return resolved
    client_user_id = resolved["client_user_id"]  # type: ignore

    coverage_months = int(opts.get("coverage_months") or 12)
    bi = _derive_bank_income(client_user_id, coverage_months, opts.get("force_mode"))
    streams = (bi.streams if bi else [])
    sum_avg = round(sum(s.average_net for s in streams), 2) if streams else 0.0
    totals = {"sum_average_net": sum_avg, "coverage_months": coverage_months, "coverage": (bi.coverage if bi else "EMPTY")}
    pdf_bytes = generate_bank_income_pdf(client_user_id, [s.model_dump() for s in streams], totals)
    return Response(content=pdf_bytes, media_type="application/pdf")


@app.post("/credit/bank_income/refresh", response_model=BankIncomeRefreshResponse)
async def bank_income_refresh(request: Request, body: AccessTokenRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        return err
    return {"refreshed_at": now_iso(), "status": "OK", "request_id": request.state.request_id}


@app.post("/credit/employment/get", response_model=EmploymentResponse)
async def employment_get(request: Request, body: AccessTokenRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        return err
    rid = request.state.request_id
    resolved = _require_item(body)
    if isinstance(resolved, dict) and "error_type" in resolved:
        resolved["request_id"] = rid
        return resolved
    client_user_id = resolved["client_user_id"]  # type: ignore
    emp = _derive_employment(client_user_id)
    return {"employment": emp.model_dump(), "request_id": rid}


@app.post("/webhooks/plaid-income", response_model=RequestIdOnly)
async def webhook_receiver(request: Request):
    rid = request.state.request_id
    body = await request.json()
    store.append_webhook("received", None, body)
    return {"request_id": rid}


@app.post("/sandbox/income/fire_webhook", response_model=RequestIdOnly)
async def sandbox_fire_webhook(request: Request, body: FireWebhookRequest):
    ok, err = validate_auth(dict(request.headers), body.model_dump())
    if not ok:
        return err
    rid = request.state.request_id

    payload = body.body or {
        "webhook_type": "INCOME",
        "webhook_code": body.webhook_code,
        "item_id": body.item_id,
        "timestamp": now_iso(),
        "request_id": rid,
    }
    store.append_webhook("sent", body.target, payload)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(body.target, json=payload)
    except Exception as e:
        logger.warning("Webhook POST failed: %s", e)

    return {"request_id": rid}


@app.get("/")
async def root():
    return {"status": "ok", "service": "mock-plaid-income"}


# UVicorn entrypoint:
# uvicorn Plaid_API.main:app --reload
