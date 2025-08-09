from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..config import settings
from ..models import (
    AMLRequest,
    AMLResponseData,
    AppliedRule,
    DeviceDetails,
    EmailBreach,
    EmailDetails,
    FraudRequest,
    FraudResponseData,
    GeoDetails,
    IpDetails,
    PhoneDetails,
    ScenarioEnum,
)


# ----------------- Deterministic helpers -----------------


def _stable_seed(*parts: Optional[str]) -> int:
    key = "|".join(p or "" for p in parts)
    h = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big", signed=False)


def _rng(email: Optional[str], ip: Optional[str], session: Optional[str]) -> random.Random:
    return random.Random(_stable_seed(email, ip, session))


def _domain(email: Optional[str]) -> Optional[str]:
    if not email or "@" not in email:
        return None
    return email.split("@", 1)[1].lower()


def _round(x: float, ndigits: int = 2) -> float:
    return round(x, ndigits)


# ----------------- Scenario selection -----------------


def derive_scenario(email: Optional[str], custom_fields: Optional[Dict[str, Any]]) -> ScenarioEnum:
    if custom_fields:
        s = str(custom_fields.get("scenario", "")).strip().lower()
        if s in {e.value for e in ScenarioEnum}:
            return ScenarioEnum(s)  # type: ignore[arg-type]
    dom = _domain(email) or ""
    if dom.endswith("good.com"):
        return ScenarioEnum.PASS
    if dom.endswith("maybe.com"):
        return ScenarioEnum.REVIEW
    if dom.endswith("fraud.com"):
        return ScenarioEnum.KO_FRAUD
    if dom.endswith("sanction.com"):
        return ScenarioEnum.KO_COMPLIANCE
    return ScenarioEnum.PASS


# ----------------- ID builders -----------------


def _txn_id(email: Optional[str], ip: Optional[str], session: Optional[str]) -> str:
    # txn_ + first 16 hex chars of sha256 for determinism
    raw = hashlib.sha256(f"{email}|{ip}|{session}".encode("utf-8")).hexdigest()
    return f"txn_{raw[:16]}"


def _seon_id(email: Optional[str], ip: Optional[str], session: Optional[str]) -> int:
    return _stable_seed(email, ip, session) % 900_000 + 100_000


# ----------------- Detail builders -----------------


def _build_ip_details(r: random.Random, req: FraudRequest, scenario: ScenarioEnum) -> IpDetails:
    # Simple country/isp inference; if user_country provided, mirror it
    country = (req.user_country or "US").upper()
    isp_pool = ["Comcast", "AT&T", "Verizon", "T-Mobile", "Vodafone", "Orange", "Cloudflare", "Akamai"]
    isp = r.choice(isp_pool)
    ip_type = "RESIDENTIAL"
    proxy = False
    vpn = False
    tor = False
    if scenario in (ScenarioEnum.REVIEW, ScenarioEnum.KO_FRAUD):
        # More suspicious network
        vpn = scenario == ScenarioEnum.KO_FRAUD or r.random() < 0.4
        proxy = True if scenario == ScenarioEnum.KO_FRAUD else r.random() < 0.35
        ip_type = "DCH" if scenario == ScenarioEnum.KO_FRAUD else r.choice(["RESIDENTIAL", "DCH"])
        if scenario == ScenarioEnum.KO_FRAUD and r.random() < 0.15:
            tor = True
        if ip_type == "DCH":
            isp = r.choice(["DigitalOcean", "AWS", "GCP", "Azure", "OVH", "Hetzner"])
    return IpDetails(country=country, isp=isp, ip_type=ip_type, proxy=proxy, vpn=vpn, tor=tor)


def _build_email_details(r: random.Random, req: FraudRequest, scenario: ScenarioEnum) -> EmailDetails:
    email = req.email
    dom = _domain(email)
    free_domains = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "maybe.com", "good.com"}
    disposable_domains = {"mailinator.com", "10minutemail.com", "tempmail.com", "sharklasers.com"}
    minimum_age_months = r.randint(1, 120) if scenario != ScenarioEnum.PASS else r.randint(24, 120)
    # scenario nudges: young age for review/fraud
    if scenario in (ScenarioEnum.REVIEW, ScenarioEnum.KO_FRAUD):
        minimum_age_months = r.randint(1, 24)
    breaches = []
    if dom in {"yahoo.com", "gmail.com"} and r.random() < (0.15 if scenario == ScenarioEnum.PASS else 0.3):
        breaches.append(EmailBreach(name="SampleBreach", year=r.choice([2016, 2019, 2021])))
    return EmailDetails(
        email=email,
        domain=dom,
        free=(dom in free_domains) if dom else False,
        disposable=(dom in disposable_domains) if dom else False,
        minimum_age_months=minimum_age_months,
        breach_details=breaches,
    )


def _build_phone_details(r: random.Random, req: FraudRequest, scenario: ScenarioEnum) -> PhoneDetails:
    provider = r.choice(["Twilio", "AT&T", "Verizon", "T-Mobile", "Orange", "Vodafone", "BT"])
    carrier = r.choice(["AT&T", "Verizon", "T-Mobile", "Orange", "Vodafone", "BT"])
    typ = "MOBILE"
    if scenario in (ScenarioEnum.REVIEW,) and r.random() < 0.5:
        typ = "VOIP"
    if scenario == ScenarioEnum.KO_FRAUD:
        typ = "VOIP"
    valid = True if scenario != ScenarioEnum.KO_FRAUD else r.random() < 0.8
    risk = {
        ScenarioEnum.PASS: r.uniform(1, 20),
        ScenarioEnum.REVIEW: r.uniform(40, 70),
        ScenarioEnum.KO_FRAUD: r.uniform(75, 95),
        ScenarioEnum.KO_COMPLIANCE: r.uniform(30, 60),
    }[scenario]
    return PhoneDetails(provider=provider, carrier=carrier, type=typ, valid=valid, risk_score=_round(risk))


def _build_device_details(r: random.Random, req: FraudRequest, scenario: ScenarioEnum) -> DeviceDetails:
    os_ = r.choice(["iOS", "Android", "Windows", "macOS", "Linux"])
    dtype = r.choice(["mobile", "desktop", "tablet"])
    browser = r.choice(["Chrome", "Safari", "Firefox", "Edge", "Samsung Internet"])
    vpn = scenario in (ScenarioEnum.REVIEW, ScenarioEnum.KO_FRAUD) and r.random() < (0.3 if scenario == ScenarioEnum.REVIEW else 0.8)
    proxy = scenario == ScenarioEnum.KO_FRAUD or (scenario == ScenarioEnum.REVIEW and r.random() < 0.25)
    flags = []
    if scenario == ScenarioEnum.KO_FRAUD:
        flags += ["device_farm_pattern", "multiple_accounts", "automation_signals"]
    elif scenario == ScenarioEnum.REVIEW:
        flags += ["new_device", "inconsistent_fingerprint"]
    session_id = req.session or None
    return DeviceDetails(os=os_, type=dtype, browser=browser, session_id=session_id, vpn=vpn, proxy=proxy, suspicious_flags=flags)


def _build_geo_details(r: random.Random, req: FraudRequest, scenario: ScenarioEnum) -> GeoDetails:
    # Mirror inputs where possible; random but stable lat/lon per seed
    country = (req.user_country or "US").upper()
    region = req.user_city or "N/A"
    city = req.user_city or r.choice(["New York", "San Francisco", "Austin", "London", "Paris", "Berlin"])
    lat = r.uniform(-60, 60)
    lon = r.uniform(-140, 140)
    accuracy_km = r.randint(5, 50) if scenario == ScenarioEnum.PASS else r.randint(20, 150)
    return GeoDetails(country=country, region=region, city=city, lat=_round(lat, 4), lon=_round(lon, 4), accuracy_km=accuracy_km)


def _applied_rules(r: random.Random, scenario: ScenarioEnum) -> List[AppliedRule]:
    palette: List[Tuple[str, str]] = []
    if scenario == ScenarioEnum.PASS:
        palette = [
            ("Velocity normal", "add"),
            ("Device consistent with history", "add"),
            ("Email domain aged", "add"),
        ]
        base = (15, 35)
    elif scenario == ScenarioEnum.REVIEW:
        palette = [
            ("VOIP carrier detected", "add"),
            ("New email domain", "add"),
            ("Geo-IP mismatch", "add"),
        ]
        base = (70, 85)
    elif scenario == ScenarioEnum.KO_FRAUD:
        palette = [
            ("Public proxy detected", "add"),
            ("Datacenter IP (DCH)", "add"),
            ("Device farm pattern", "add"),
        ]
        base = (90, 98)
    else:  # KO_COMPLIANCE
        palette = [
            ("Sanctions indicator match", "add"),
            ("PEP potential", "add"),
            ("Watchlist name similarity", "add"),
        ]
        base = (90, 98)

    rules: List[AppliedRule] = []
    for idx, (name, op) in enumerate(palette, start=1):
        rid = f"R-{1000 + idx}"
        score = r.uniform(3, 15) if scenario == ScenarioEnum.PASS else r.uniform(8, 25)
        rules.append(AppliedRule(id=rid, name=name, operation=op, score=_round(score, 2)))
    return rules


# ----------------- Public builders -----------------


def build_fraud_data(req: FraudRequest) -> FraudResponseData:
    scenario = derive_scenario(req.email, req.custom_fields)
    r = _rng(req.email, req.ip, req.session)

    # Scores and state by scenario
    state = {"pass": "APPROVE", "review": "REVIEW", "ko_fraud": "DECLINE", "ko_compliance": "DECLINE"}[scenario.value]
    fs_min, fs_max = {
        ScenarioEnum.PASS: (15, 35),
        ScenarioEnum.REVIEW: (70, 85),
        ScenarioEnum.KO_FRAUD: (90, 98),
        ScenarioEnum.KO_COMPLIANCE: (90, 98),
    }[scenario]
    fraud_score = _round(r.uniform(fs_min, fs_max), 2)
    blackbox_score = _round(r.uniform(0, 100), 2)
    calc_ms = r.randint(120, 450)

    ip_details = _build_ip_details(r, req, scenario)
    email_details = _build_email_details(r, req, scenario)
    phone_details = _build_phone_details(r, req, scenario)
    device_details = _build_device_details(r, req, scenario)
    geo_details = _build_geo_details(r, req, scenario)
    rules = _applied_rules(r, scenario)

    # If KO_COMPLIANCE, ensure applied_rules mention AML reasons
    if scenario == ScenarioEnum.KO_COMPLIANCE and all("Sanction" not in x.name for x in rules):
        rules.append(AppliedRule(id="R-2001", name="Sanction list disqualifier", operation="add", score=25.0))

    return FraudResponseData(
        id=_txn_id(req.email, req.ip, req.session),
        state=state,
        fraud_score=fraud_score,
        blackbox_score=blackbox_score,
        applied_rules=rules,
        ip_details=ip_details,
        email_details=email_details,
        phone_details=phone_details,
        device_details=device_details,
        geolocation_details=geo_details,
        calculation_time=calc_ms,
        seon_id=_seon_id(req.email, req.ip, req.session),
    )


def build_aml_data(req: AMLRequest) -> AMLResponseData:
    # Prefer custom_fields.scenario; else infer from email heuristic if provided
    scenario = derive_scenario(req.email, req.custom_fields)
    if scenario == ScenarioEnum.KO_FRAUD:
        # Fraud KO treated as pass in AML
        scenario = ScenarioEnum.PASS

    r = _rng(req.email, None, None)

    has_watchlist_match = False
    has_sanction_match = False
    has_crimelist_match = False
    has_pep_match = False
    has_adversemedia_match = False
    result_payload: Dict[str, Any] = {}

    if scenario == ScenarioEnum.PASS:
        pass
    elif scenario == ScenarioEnum.REVIEW:
        has_adversemedia_match = True
        result_payload["adverse_media"] = [
            {
                "title": "Customer named in minor blog report",
                "source": "BlogSite",
                "url": "https://example.com/article",
                "ts": "2024-03-10T12:34:56Z",
            }
        ]
    elif scenario == ScenarioEnum.KO_COMPLIANCE:
        has_sanction_match = True
        has_watchlist_match = True if r.random() < 0.5 else False
        has_pep_match = True if r.random() < 0.4 else False
        result_payload["sanctions"] = [
            {
                "list": r.choice(["OFAC-SDN", "EU-Consolidated", "UN-Sanctions"]),
                "name": req.user_fullname,
                "match_score": _round(r.uniform(0.85, 0.97), 2),
                "country": (req.user_country or "US").upper(),
            },
            {
                "list": "Interpol-Warn",
                "name": f"{req.user_fullname} (aka)",
                "match_score": _round(r.uniform(0.72, 0.9), 2),
                "country": (req.user_country or "US").upper(),
            },
        ]
        if has_pep_match:
            result_payload["pep"] = [
                {"name": req.user_fullname, "role": r.choice(["Mayor", "Advisor", "Board Member"]), "tier": r.randint(1, 4)}
            ]

    local_aml_match = {"matched": has_sanction_match or has_pep_match or has_watchlist_match, "notes": None}

    return AMLResponseData(
        has_watchlist_match=has_watchlist_match,
        has_sanction_match=has_sanction_match,
        has_crimelist_match=has_crimelist_match,
        has_pep_match=has_pep_match,
        has_adversemedia_match=has_adversemedia_match,
        local_aml_match=local_aml_match,
        result_payload=result_payload,
    )
