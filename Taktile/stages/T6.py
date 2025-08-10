from typing import Any, Dict, Optional, Tuple


def _cadence_factor(cadence: Optional[str]) -> float:
    c = (cadence or "").upper()
    if c == "WEEKLY":
        return 4.33
    if c == "BIWEEKLY":
        return 2.17  # ~26 / 12
    if c == "SEMIMONTHLY":
        return 2.0
    if c == "MONTHLY":
        return 1.0
    return 1.0


def _net_monthly_from_payroll(payroll_income: Optional[Dict[str, Any]]) -> Optional[float]:
    if not payroll_income:
        return None
    streams = payroll_income.get("streams") or []
    if not streams:
        return None
    s0 = streams[0] or {}
    net = float(s0.get("net") or 0.0)
    cadence = s0.get("cadence") or payroll_income.get("pay_frequency")
    return round(net * _cadence_factor(cadence), 2)


def _net_monthly_from_bank(bank_income: Optional[Dict[str, Any]]) -> Optional[float]:
    if not bank_income:
        return None
    streams = bank_income.get("streams") or []
    if not streams:
        return None
    s0 = streams[0] or {}
    # In our mock, average_net is monthly already; if it were per deposit we'd multiply by cadence factor
    avg_net = float(s0.get("average_net") or 0.0)
    return round(avg_net, 2)


def _income_tier_from_net_monthly(net_monthly: float) -> int:
    # 7: ≥5000, 6: 3500–4999, 5: 2500–3499, 4: 1800–2499, 3: 1400–1799, 2: 1000–1399, 1: 800–999, 0: <800
    nm = float(net_monthly)
    if nm >= 5000:
        return 7
    if nm >= 3500:
        return 6
    if nm >= 2500:
        return 5
    if nm >= 1800:
        return 4
    if nm >= 1400:
        return 3
    if nm >= 1000:
        return 2
    if nm >= 800:
        return 1
    return 0


def _has_plaid_error(resp: Optional[Dict[str, Any]]) -> bool:
    if not isinstance(resp, dict):
        return False
    return bool(resp.get("error_type") or resp.get("error_code"))


def evaluate_income(
    payroll_resp: Optional[Dict[str, Any]],
    bank_resp: Optional[Dict[str, Any]],
    risk_resp: Optional[Dict[str, Any]],
    coverage_months: int,
    credit_final_tier: Optional[int],
) -> Dict[str, Any]:
    """
    Apply KO/Review/Pass rules per docs/income criteria.txt.

    Inputs: raw Plaid mock JSONs for payroll, bank, and risk signals (may be None), coverage_months requested,
    and the final tier after credit (to merge conservatively on pass).
    """
    reasons: list[str] = []
    review_reasons: list[str] = []

    # Detect vendor-style errors → Review
    if _has_plaid_error(payroll_resp) or _has_plaid_error(bank_resp) or _has_plaid_error(risk_resp):
        return {
            "decision": "INCOME_REVIEW",
            "source_used": "unknown",
            "reasons": [],
            "review_reasons": ["vendor_error"],
            "metrics": {},
            "income_tier": None,
            "final_tier": None,
            "has_pdf": False,
        }

    payroll_income = (payroll_resp or {}).get("payroll_income") if isinstance(payroll_resp, dict) else None
    bank_income = (bank_resp or {}).get("bank_income") if isinstance(bank_resp, dict) else None

    risk_signals = []
    if isinstance(risk_resp, dict):
        risk_signals = risk_resp.get("signals") or []
    is_suspicious = any((s.get("code") or "").upper() != "NO_FINDINGS" and (s.get("severity") or "LOW") in ("MEDIUM", "HIGH") for s in risk_signals)

    # Choose source
    source_used = "empty"
    net_monthly: Optional[float] = None
    coverage = None

    if payroll_income:
        source_used = "payroll"
        net_monthly = _net_monthly_from_payroll(payroll_income)
    elif bank_income:
        source_used = "bank"
        net_monthly = _net_monthly_from_bank(bank_income)
        coverage = bank_income.get("coverage")

    # KO rules
    # 1) No income at all
    if not net_monthly or net_monthly <= 0:
        return {
            "decision": "INCOME_DECLINE",
            "source_used": source_used,
            "reasons": ["NO_INCOME"],
            "review_reasons": [],
            "metrics": {"net_monthly": net_monthly or 0.0, "coverage": coverage or "EMPTY", "coverage_months": coverage_months},
            "income_tier": None,
            "final_tier": None,
            "has_pdf": False,
        }

    # 2) Net monthly too low (< 1000)
    if net_monthly < 1000:
        return {
            "decision": "INCOME_DECLINE",
            "source_used": source_used,
            "reasons": ["NET_MONTHLY_LT_1000"],
            "review_reasons": [],
            "metrics": {"net_monthly": net_monthly, "coverage": coverage or "N/A", "coverage_months": coverage_months},
            "income_tier": None,
            "final_tier": None,
            "has_pdf": False,
        }

    # 3) Suspicious + net monthly < 1500
    if is_suspicious and net_monthly < 1500:
        return {
            "decision": "INCOME_DECLINE",
            "source_used": source_used,
            "reasons": ["SUSPICIOUS_AND_LOW_INCOME"],
            "review_reasons": [],
            "metrics": {"net_monthly": net_monthly, "coverage": coverage or "N/A", "coverage_months": coverage_months},
            "income_tier": None,
            "final_tier": None,
            "has_pdf": False,
        }

    # 4) Bank fallback coverage thin
    if source_used == "bank":
        cov = (coverage or "").upper()
        if (cov != "FULL") and (coverage_months < 3):
            return {
                "decision": "INCOME_DECLINE",
                "source_used": source_used,
                "reasons": ["INSUFFICIENT_COVERAGE"],
                "review_reasons": [],
                "metrics": {"net_monthly": net_monthly, "coverage": coverage or "EMPTY", "coverage_months": coverage_months},
                "income_tier": None,
                "final_tier": None,
                "has_pdf": False,
            }

    # Review triggers (non-KO)
    if is_suspicious and net_monthly >= 1500:
        review_reasons.append("SUSPICIOUS_SIGNALS")
    # Additional review hooks could include PDF fetch failure or employment mismatch.

    # Compute tier and merge
    income_tier = _income_tier_from_net_monthly(net_monthly)

    # Decide pass/review
    decision = "INCOME_PASS" if not review_reasons else "INCOME_REVIEW"

    # Enforce tier policy:
    # - No final tier unless this stage passes AND a prior credit tier exists
    # - No income tier exposed on review/decline paths
    if decision == "INCOME_PASS":
        income_tier_out = int(income_tier)
        final_tier = min(int(credit_final_tier), int(income_tier)) if credit_final_tier is not None else None
    else:
        income_tier_out = None
        final_tier = None

    # Compute credit limit (8x monthly income) only on pass
    credit_limit = round(net_monthly * 8, 2) if decision == "INCOME_PASS" else None

    return {
        "decision": decision,
        "source_used": source_used,
        "reasons": reasons,
        "review_reasons": review_reasons,
        "metrics": {"net_monthly": net_monthly, "coverage": coverage or ("N/A" if source_used == "payroll" else "EMPTY"), "coverage_months": coverage_months},
        "income_tier": income_tier_out,
        "final_tier": final_tier,
        "credit_limit": credit_limit,
        "has_pdf": False,
    }
