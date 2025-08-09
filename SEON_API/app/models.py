from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ScenarioEnum(str, Enum):
    PASS = "pass"
    REVIEW = "review"
    KO_FRAUD = "ko_fraud"
    KO_COMPLIANCE = "ko_compliance"


# ---------- Common detail blocks ----------


class AppliedRule(BaseModel):
    id: str
    name: str
    operation: str
    score: float


class DeviceDetails(BaseModel):
    os: str
    type: str
    browser: str
    session_id: Optional[str] = None
    vpn: bool = False
    proxy: bool = False
    suspicious_flags: List[str] = Field(default_factory=list)


class EmailBreach(BaseModel):
    name: str
    year: int


class EmailDetails(BaseModel):
    email: Optional[str] = None
    domain: Optional[str] = None
    free: bool = False
    disposable: bool = False
    minimum_age_months: int = 0
    breach_details: List[EmailBreach] = Field(default_factory=list)


class PhoneDetails(BaseModel):
    provider: str
    carrier: str
    type: str  # "MOBILE" | "VOIP"
    valid: bool
    risk_score: float


class IpDetails(BaseModel):
    country: str
    isp: str
    ip_type: str  # "DCH" | "RESIDENTIAL"
    proxy: bool = False
    vpn: bool = False
    tor: bool = False


class GeoDetails(BaseModel):
    country: str
    region: str
    city: str
    lat: float
    lon: float
    accuracy_km: int


# ---------- Fraud API ----------


class FraudRequest(BaseModel):
    # Known fields (others allowed)
    email: Optional[str] = None
    phone_number: Optional[str] = None
    ip: Optional[str] = None
    user_fullname: Optional[str] = None
    user_dob: Optional[str] = None
    user_country: Optional[str] = None
    user_city: Optional[str] = None
    user_zip: Optional[str] = None
    user_street: Optional[str] = None
    session: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None

    model_config = {"extra": "allow"}


class FraudResponseData(BaseModel):
    id: str
    state: str  # "APPROVE" | "REVIEW" | "DECLINE"
    fraud_score: float
    blackbox_score: float
    version: str = "v2"
    applied_rules: List[AppliedRule] = Field(default_factory=list)
    ip_details: IpDetails
    email_details: EmailDetails
    phone_details: PhoneDetails
    device_details: DeviceDetails
    geolocation_details: GeoDetails
    calculation_time: int
    seon_id: int


# ---------- AML API ----------


class AMLRequest(BaseModel):
    user_fullname: str
    user_dob: Optional[str] = None
    user_country: Optional[str] = None
    email: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None

    model_config = {"extra": "allow"}


class AMLResponseData(BaseModel):
    has_watchlist_match: bool
    has_sanction_match: bool
    has_crimelist_match: bool
    has_pep_match: bool
    has_adversemedia_match: bool
    local_aml_match: Dict[str, Any]
    result_payload: Dict[str, Any]


# ---------- Lists / Labels / Exclusion ----------


class ListEntryIn(BaseModel):
    data_field: str  # e.g., "ip" | "email" | "user_id"
    value: str
    state: str  # "blacklist" | "whitelist" | "normal"
    comment: Optional[str] = None
    expire_day: Optional[int] = Field(default=None, description="Days until expiry")


class ListEntryOut(BaseModel):
    data_field: str
    value: str
    state: str
    comment: Optional[str] = None
    created_at: str
    expire_at: Optional[str] = None


class LabelItem(BaseModel):
    transaction_id: str
    label: str


class ExclusionIn(BaseModel):
    user_ids: Optional[List[str]] = None
    emails: Optional[List[str]] = None
