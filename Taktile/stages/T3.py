from typing import Any, Dict, List, Optional


CONFIG = {
    "scoreFloor": 660,
    "revolvingUtilizationMax": 0.90,
    "hardInquiries6mMax": 4,
    "recentChargeoffMonths": 24,
    "recentRepoForeclosureMonths": 36,
    "recentBankruptcyMonths": 84,
    "recentCollectionsMonths": 12,
    "collectionBalanceMin": 500,
    "totalPastDueMin": 500,
    "thinFile": {"minOpenTrades": 2, "minOldestOpenMonths": 12},
}


def _months_since(date_str: Optional[str]) -> int:
    """
    Accepts: MMDDYYYY or YYYYMMDD or YYYY-MM-DD (best effort).
    Returns large number on parse failure.
    """
    if not date_str:
        return 9999
    s = str(date_str)
    iso = s
    if len(s) == 8 and s.isdigit():
        # Guess MMDDYYYY (Experian often returns MMDDYYYY or similar)
        mm, dd, yyyy = s[:2], s[2:4], s[4:8]
        iso = f"{yyyy}-{mm}-{dd}"
    try:
        from datetime import date
        parts = iso.split("-")
        if len(parts) == 3:
            yyyy, mm, dd = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            # fallback: try MMDDYYYY again
            mm, dd, yyyy = int(s[:2]), int(s[2:4]), int(s[4:8])
        d = date(yyyy, mm, dd)
        today = date.today()
        return (today.year - d.year) * 12 + (today.month - d.month)
    except Exception:
        return 9999


def _num(v: Any) -> float:
    try:
        return float(str(v).replace(",", "").replace("$", "").strip())
    except Exception:
        return 0.0


def _is_hard_inquiry(i: Dict[str, Any]) -> bool:
    t = str(i.get("type") or "").upper()
    # treat any non-soft as hard by default policy (can refine)
    return t and t != "SOFT"


def _extract_cp(data: Dict[str, Any]) -> Dict[str, Any]:
    return (data.get("creditProfile") or [{}])[0] or {}


def evaluate_credit_policy(resp: Dict[str, Any], seon_tier: Optional[int], freeze_override_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluate Experian response and produce credit decision + tiers.
    Returns:
      {
        "decision": "CREDIT_DECLINE" | "CREDIT_REVIEW" | "CREDIT_PASS",
        "bureau_tier": int,
        "final_tier": Optional[int],  # min(seon_tier, bureau_tier) if PASS
        "ko_reasons": List[str],
        "review_reasons": List[str],
        "scorecard": Dict[str, Any]
      }
    """
    # If vendor-level error present, push to review
    if not isinstance(resp, dict) or (resp.get("errors") and len(resp.get("errors")) > 0):
        return {
            "decision": "CREDIT_REVIEW",
            "bureau_tier": 0,
            "final_tier": None,
            "ko_reasons": [],
            "review_reasons": ["vendor_error_or_timeout"],
            "scorecard": {},
        }

    cp = _extract_cp(resp)
    ko_reasons: List[str] = []
    review_reasons: List[str] = []

    # OFAC match (decline)
    ofac = cp.get("ofac") or {}
    if str(ofac.get("messageText") or "").strip():
        ko_reasons.append("OFAC_MATCH")

    # Security freeze present w/o override (decline)
    statements = cp.get("statement") or []
    has_freeze_stmt = any("freeze" in str(s.get("statementText") or "").lower() for s in statements)
    if has_freeze_stmt and not freeze_override_code:
        ko_reasons.append("SECURITY_FREEZE_NO_OVERRIDE")

    # Deceased/fraud severe flags (decline)
    fraud = (cp.get("fraudShield") or [None])[0] or {}
    indicators = (fraud.get("fraudShieldIndicators") or {}).get("indicator") or []
    # indicator "5" is often severe; also treat dateOfDeath if ever present
    if fraud.get("dateOfDeath") or ("5" in [str(x) for x in indicators]):
        ko_reasons.append("DECEASED_OR_FRAUD_FLAG")

    # Bankruptcies in last 7y (84 months)
    public_records = cp.get("publicRecord") or []
    recent_bk = any(
        ("bankruptcy" in str(r.get("courtName") or "").lower())
        and _months_since(r.get("statusDate") or r.get("filingDate")) <= CONFIG["recentBankruptcyMonths"]
        for r in public_records
    )
    if recent_bk:
        ko_reasons.append("RECENT_BANKRUPTCY")

    tradelines = cp.get("tradeline") or []

    # Charge-offs in last 24 months
    recent_co = False
    for t in tradelines:
        status = f"{t.get('status') or ''} {((t.get('enhancedPaymentData') or {}).get('enhancedPaymentStatus') or '')}"
        co_amt = _num((t.get("enhancedPaymentData") or {}).get("chargeoffAmount"))
        when = t.get("statusDate") or t.get("balanceDate")
        if ("CHARGE" in status.upper() and "OFF" in status.upper()) or co_amt > 0:
            if _months_since(when) <= CONFIG["recentChargeoffMonths"]:
                recent_co = True
                break
    if recent_co:
        ko_reasons.append("RECENT_CHARGEOFF")

    # Repo/Foreclosure in last 36 months
    repo_fore = False
    for t in tradelines:
        sc = f"{t.get('specialComment') or ''} {((t.get('enhancedPaymentData') or {}).get('enhancedSpecialComment') or '')}"
        when = t.get("statusDate") or t.get("maxDelinquencyDate")
        if ("REPOSSESSION" in sc.upper() or "FORECLOSURE" in sc.upper()) and _months_since(when) <= CONFIG["recentRepoForeclosureMonths"]:
            repo_fore = True
            break
    if repo_fore:
        ko_reasons.append("RECENT_REPO_OR_FORECLOSURE")

    # 90+ DPD ≤ 12m
    d90 = False
    for t in tradelines:
        d90cnt = _num(t.get("delinquencies90to180Days"))
        when = t.get("statusDate") or t.get("maxDelinquencyDate")
        if d90cnt > 0 and _months_since(when) <= 12:
            d90 = True
            break
    if d90:
        ko_reasons.append("90DPD_LAST_12M")

    # Collections open > $500 ≤ 12m
    recent_coll = False
    for t in tradelines:
        looks_coll = "COLLECT" in f"{t.get('specialComment') or ''} {t.get('originalCreditorName') or ''}".upper()
        bal = _num(t.get("balanceAmount"))
        when = t.get("openDate") or t.get("statusDate") or t.get("balanceDate")
        if looks_coll and bal > CONFIG["collectionBalanceMin"] and _months_since(when) <= CONFIG["recentCollectionsMonths"]:
            recent_coll = True
            break
    if recent_coll:
        ko_reasons.append("RECENT_COLLECTION_GT_500")

    # Revolving utilization > 90% (decline)
    open_rev = [t for t in tradelines if t.get("revolvingOrInstallment") == "R" and t.get("openOrClosed") == "O"]
    tot_bal = sum(_num(t.get("balanceAmount")) for t in open_rev)
    tot_lim = sum(_num((t.get("enhancedPaymentData") or {}).get("creditLimitAmount")) for t in open_rev)
    utilization = (tot_bal / tot_lim) if tot_lim > 0 else 0.0
    if tot_lim > 0 and utilization > CONFIG["revolvingUtilizationMax"]:
        ko_reasons.append("REV_UTIL_GT_90")

    # Total past due > $500 and multiple past-due
    tot_past_due = sum(_num(t.get("amountPastDue")) for t in tradelines)
    if tot_past_due > CONFIG["totalPastDueMin"]:
        ko_reasons.append("TOTAL_PAST_DUE_GT_500")
    num_past_due = sum(1 for t in tradelines if _num(t.get("amountPastDue")) > 0)
    if num_past_due > 1:
        ko_reasons.append("MULTIPLE_PAST_DUE")

    # Hard inquiries > threshold in last 6 months
    inquiries = cp.get("inquiry") or []
    hard6m = sum(1 for i in inquiries if _is_hard_inquiry(i) and _months_since(i.get("date")) <= 6)
    if hard6m > CONFIG["hardInquiries6mMax"]:
        ko_reasons.append("EXCESSIVE_HARD_INQUIRIES_6M")

    # Thin & young file
    open_trades = [t for t in tradelines if t.get("openOrClosed") == "O"]
    oldest_open_months = min([_months_since(t.get("openDate") or "19000101") for t in open_trades] or [9999])
    if len(open_trades) < CONFIG["thinFile"]["minOpenTrades"] and oldest_open_months < CONFIG["thinFile"]["minOldestOpenMonths"]:
        ko_reasons.append("THIN_AND_YOUNG_FILE")

    # Score floor
    risk_models = cp.get("riskModel") or []
    model = None
    for m in risk_models:
        ind = str(m.get("modelIndicator") or "").upper()
        if "V4" in ind or "FICO" in ind:
            model = m
            break
    base_score = _num((model or {}).get("score"))
    if model and base_score < CONFIG["scoreFloor"]:
        ko_reasons.append("SCORE_BELOW_FLOOR")

    # If any KO, we decline
    if ko_reasons:
        scorecard = _build_scorecard(model, utilization, hard6m, tradelines, open_rev)
        return {
            "decision": "CREDIT_DECLINE",
            "bureau_tier": 0,
            "final_tier": None,
            "ko_reasons": ko_reasons,
            "review_reasons": [],
            "scorecard": scorecard,
        }

    # Compute contribution score for tiering
    c_score = 100.0
    contributions: Dict[str, float] = {}

    # Base from score band
    score_band = 0.0
    if base_score >= 780:
        score_band = +5
    elif base_score >= 740:
        score_band = 0
    elif base_score >= 700:
        score_band = -5
    elif base_score >= 660:
        score_band = -10
    elif base_score >= 640:
        score_band = -15
    elif base_score >= 620:
        score_band = -20
    else:
        score_band = -30
    c_score += score_band
    contributions["scoreBand"] = score_band

    # Utilization (we know it's <= 90% here)
    util_adj = 0.0
    if utilization > 0 and utilization <= 0.09:
        util_adj = +3
    elif 0.30 <= utilization <= 0.49:
        util_adj = -5
    elif 0.50 <= utilization <= 0.79:
        util_adj = -10
    elif 0.80 <= utilization <= 0.89:
        util_adj = -15
    c_score += util_adj
    contributions["revolvingUtilization"] = util_adj

    # Delinquency (non-90) in last 24m
    any60 = any(_num(t.get("delinquencies60Days")) > 0 for t in tradelines)
    any30_count = sum(1 for t in tradelines if _num(t.get("delinquencies30Days")) > 0)
    del_adj = 0.0
    if any60:
        del_adj = -20
    elif any30_count > 0:
        # up to -16 in total for multiple 30s
        del_adj = -min(16, any30_count * 8)
    c_score += del_adj
    contributions["delinquency24m"] = del_adj

    # Inquiries 6m
    inq_adj = 0.0
    if hard6m == 0:
        inq_adj = +2
    elif hard6m <= 2:
        inq_adj = -2
    elif hard6m <= 4:
        inq_adj = -5
    c_score += inq_adj
    contributions["inquiries6m"] = inq_adj

    # Age/depth
    oldest_trade_months = min([_months_since(t.get("openDate") or "19000101") for t in tradelines] or [9999])
    age_adj = 0.0
    if oldest_trade_months >= 84:
        age_adj = +5
    elif oldest_trade_months >= 36:
        age_adj = +2
    elif oldest_trade_months < 12:
        age_adj = -8
    c_score += age_adj
    contributions["ageDepth"] = age_adj

    # Mix
    has_rev = any(t.get("revolvingOrInstallment") == "R" for t in tradelines)
    has_inst = any(t.get("revolvingOrInstallment") == "I" for t in tradelines)
    has_mort = any("MORTGAGE" in str(t.get("accountType") or "").upper() for t in tradelines)
    mix_adj = 0.0
    if has_rev and has_inst:
        mix_adj += 3
    if has_mort:
        mix_adj += 3
    c_score += mix_adj
    contributions["creditMix"] = mix_adj

    # Tier mapping
    if c_score >= 95:
        bureau_tier = 7
    elif c_score >= 90:
        bureau_tier = 6
    elif c_score >= 85:
        bureau_tier = 5
    elif c_score >= 80:
        bureau_tier = 4
    elif c_score >= 75:
        bureau_tier = 3
    elif c_score >= 70:
        bureau_tier = 2
    elif c_score >= 60:
        bureau_tier = 1
    else:
        bureau_tier = 0

    # Review flags
    if not model:
        review_reasons.append("NO_RISK_MODEL_SCORE")
    disputed = any(str(t.get("consumerDisputeFlag") or "") for t in tradelines)
    if disputed:
        review_reasons.append("DISPUTED_TRADELINES")

    final_decision = "CREDIT_PASS"
    if review_reasons:
        final_decision = "CREDIT_REVIEW"

    scorecard = _build_scorecard(model, utilization, hard6m, tradelines, open_rev, contributions)
    final_tier = min(int(seon_tier or 0), int(bureau_tier)) if final_decision == "CREDIT_PASS" else None

    return {
        "decision": final_decision,
        "bureau_tier": bureau_tier,
        "final_tier": final_tier,
        "ko_reasons": ko_reasons,
        "review_reasons": review_reasons,
        "scorecard": scorecard,
    }


def _build_scorecard(model: Optional[Dict[str, Any]], utilization: float, hard6m: int, tradelines: List[Dict[str, Any]], open_rev: List[Dict[str, Any]], contributions: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    oldest_trade_months = min([_months_since(t.get("openDate") or "19000101") for t in tradelines] or [9999])
    return {
        "modelUsed": (model or {}).get("modelIndicator"),
        "baseScore": _num((model or {}).get("score")) if model else None,
        "revolvingUtilization": round(utilization, 3) if utilization else 0.0,
        "inquiries6m": hard6m,
        "oldestTradeMonths": oldest_trade_months,
        "creditMix": {
            "revolving": len(open_rev) > 0,
            "installment": any(t.get("revolvingOrInstallment") == "I" for t in tradelines),
            "mortgage": any("MORTGAGE" in str(t.get("accountType") or "").upper() for t in tradelines),
        },
        "contributions": contributions or {},
    }
