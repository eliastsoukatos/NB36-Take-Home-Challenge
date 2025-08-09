from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# Common -----------------------------------------------------------------------------

class Options(BaseModel):
    force_mode: Optional[Literal["payroll", "bank", "document", "empty"]] = None
    coverage_months: Optional[int] = Field(default=12, ge=1, le=60)
    risk_profile: Optional[Literal["clean", "suspicious"]] = None
    inject_error: Optional[str] = None


class AuthBody(BaseModel):
    client_id: Optional[str] = None
    secret: Optional[str] = None


class RequestIdOnly(BaseModel):
    request_id: str


# Users / Link / Item ----------------------------------------------------------------

class UserCreateRequest(AuthBody):
    client_user_id: str


class UserCreateResponse(RequestIdOnly):
    user_id: str


class LinkTokenCreateRequest(AuthBody):
    client_name: Optional[str] = None
    language: Optional[str] = None
    country_codes: Optional[List[str]] = None
    user: Dict[str, Any]
    products: Optional[List[str]] = None
    webhook: Optional[str] = None


class LinkTokenCreateResponse(RequestIdOnly):
    link_token: str
    expiration: str


class ItemPublicTokenExchangeRequest(AuthBody):
    public_token: str
    client_user_id: Optional[str] = None


class ItemPublicTokenExchangeResponse(RequestIdOnly):
    access_token: str
    item_id: str


# Access-token based requests ---------------------------------------------------------

class AccessTokenRequest(AuthBody):
    access_token: Optional[str] = None
    client_user_id: Optional[str] = None
    options: Optional[Options] = None


class CreditSessionsGetRequest(AuthBody):
    session_id: Optional[str] = None
    options: Optional[Options] = None
    metadata: Optional[Dict[str, Any]] = None


# Webhooks ---------------------------------------------------------------------------

class FireWebhookRequest(AuthBody):
    webhook_code: str
    item_id: str
    target: str
    body: Optional[Dict[str, Any]] = None  # optional custom body override


class WebhookAck(RequestIdOnly):
    ok: bool = True


# Income/Employment response sketches (plausible) ------------------------------------

class PayrollStream(BaseModel):
    label: str
    cadence: Literal["WEEKLY", "BIWEEKLY", "SEMIMONTHLY", "MONTHLY"]
    gross: float
    net: float


class PayrollIncome(BaseModel):
    employer: str
    pay_frequency: Literal["WEEKLY", "BIWEEKLY", "SEMIMONTHLY", "MONTHLY"]
    ytd_gross: float
    streams: List[PayrollStream]


class PayrollIncomeResponse(RequestIdOnly):
    payroll_income: Optional[PayrollIncome] = None  # may be None for empty/force


class RiskSignal(BaseModel):
    code: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    description: str


class PayrollRiskSignalsResponse(RequestIdOnly):
    signals: List[RiskSignal]


class BankStream(BaseModel):
    source: Literal["Direct deposit", "Unknown", "Other"]
    cadence: Literal["WEEKLY", "BIWEEKLY", "SEMIMONTHLY", "MONTHLY"]
    average_net: float
    confidence: Literal["LOW", "MEDIUM", "HIGH"]


class BankIncome(BaseModel):
    coverage: Literal["FULL", "PARTIAL", "EMPTY"]
    streams: List[BankStream]


class BankIncomeResponse(RequestIdOnly):
    bank_income: Optional[BankIncome] = None


class BankIncomeRefreshResponse(RequestIdOnly):
    refreshed_at: str
    status: Literal["OK"]


class EmploymentRecord(BaseModel):
    employer: str
    status: Literal["ACTIVE", "INACTIVE"]
    hire_date: str


class EmploymentResponse(RequestIdOnly):
    employment: EmploymentRecord


class CreditSessionMeta(RequestIdOnly):
    session_id: Optional[str] = None
    echo: Optional[Dict[str, Any]] = None
    results: Dict[str, Any]
