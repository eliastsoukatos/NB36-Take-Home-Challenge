from typing import Any, Dict, List


def _has_severe_flags(data: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []

    # Device details
    dd = (data.get("device_details") or {}) if isinstance(data.get("device_details"), dict) else {}
    if dd.get("vpn"):
        reasons.append("device_vpn")
    if dd.get("proxy"):
        reasons.append("device_proxy")
    # Heuristic: emulator/bot flags often captured as suspicious_flags list
    for flag in dd.get("suspicious_flags", []) or []:
        f = str(flag).lower()
        if any(k in f for k in ["emulator", "bot", "automation"]):
            reasons.append("device_emulator_or_bot")
            break

    # IP details
    ipd = (data.get("ip_details") or {}) if isinstance(data.get("ip_details"), dict) else {}
    ip_type = (ipd.get("ip_type") or "").upper()
    if ip_type == "DCH":
        reasons.append("ip_datacenter")
    if ipd.get("proxy"):
        reasons.append("ip_proxy")
    if ipd.get("vpn"):
        reasons.append("ip_vpn")
    if ipd.get("tor"):
        reasons.append("ip_tor")

    # Basic presence checks
    # If session/device missing entirely, mark as weaker signal for review bucket
    if not dd:
        reasons.append("missing_device")
    # Additional blocks could be scanned similarly (email_details/phone_details)

    return reasons


def _tier_from_score(score: float | int) -> int:
    # Lower fraud score => higher tier (7 best ... 0 base)
    try:
        s = float(score)
    except Exception:
        s = 0.0
    if s <= 30:
        return 7
    if s <= 40:
        return 6
    if s <= 50:
        return 5
    if s <= 60:
        return 4
    if s <= 70:
        return 3
    if s <= 80:
        return 2
    if s <= 90:
        return 1
    return 0


def evaluate_fraud(fraud_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: SEON Fraud API JSON (mock).
    Output:
      {
        "decision": "FRAUD_DECLINE" | "FRAUD_REVIEW" | "FRAUD_PASS",
        "provisional_tier": int | None,
        "reasons": [str, ...],
        "details": {"fraud_score": float, ...}
      }
    Logic (placeholder thresholds; tune later):
      - DECLINE if fraud_score >= 90 OR severe combo (vpn/proxy + datacenter IP + emulator/bot flags).
      - REVIEW if 70 <= fraud_score < 90 OR single severe red flag OR missing device/session.
      - PASS otherwise.
    Tier mapping (if PASS):
      - <=30: 7
      - <=40: 6
      - <=50: 5
      - <=60: 4
      - <=70: 3
      - <=80: 2
      - <=90: 1
      - else: 0
    """
    if not isinstance(fraud_response, dict) or not fraud_response.get("success"):
        return {
            "decision": "FRAUD_REVIEW",
            "provisional_tier": None,
            "reasons": ["vendor_error_or_timeout"],
            "details": {"fraud_score": None},
        }

    data = fraud_response.get("data") or {}
    fraud_score = data.get("fraud_score", 0)
    reasons = _has_severe_flags(data)

    # Decline if very high or multiple severe red flags
    try:
        score_val = float(fraud_score)
    except Exception:
        score_val = 0.0

    if score_val >= 90 or len(reasons) >= 3:
        return {
            "decision": "FRAUD_DECLINE",
            "provisional_tier": None,
            "reasons": reasons or ["high_risk_score"],
            "details": {"fraud_score": score_val},
        }

    # Review if medium-high or at least one severe flag or missing device/session
    # Note: "missing_device" is included by _has_severe_flags as a reason when device_details absent.
    if 70 <= score_val < 90 or any(reasons):
        return {
            "decision": "FRAUD_REVIEW",
            "provisional_tier": None,
            "reasons": reasons or ["medium_high_risk_score"],
            "details": {"fraud_score": score_val},
        }

    # Pass otherwise
    tier = _tier_from_score(score_val)
    return {
        "decision": "FRAUD_PASS",
        "provisional_tier": tier,
        "reasons": reasons,  # usually empty here, but include if any contextual notes exist
        "details": {"fraud_score": score_val},
    }
