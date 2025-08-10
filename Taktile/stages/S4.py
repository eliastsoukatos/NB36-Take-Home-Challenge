from typing import Any, Dict, Optional

from Taktile.clients.plaid import PlaidClient


plaid = PlaidClient()


def build_income_options_from_intake(intake: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract Plaid income options from intake.custom_fields in the shape expected by the service.
    Recognized keys:
      - income_force_mode: "payroll" | "bank"
      - income_risk_profile: e.g. "NO_FINDINGS" | "MEDIUM" | "HIGH"
      - income_inject_error: bool
      - income_coverage_months: int (defaults to 12)
    """
    cf = (intake.get("custom_fields") or {}) if isinstance(intake, dict) else {}
    options: Dict[str, Any] = {}
    if cf.get("income_force_mode"):
        options["force_mode"] = cf.get("income_force_mode")
    if cf.get("income_risk_profile"):
        options["risk_profile"] = cf.get("income_risk_profile")
    if cf.get("income_inject_error"):
        options["inject_error"] = cf.get("income_inject_error")
    # coverage_months is always passed along for the evaluator
    options["coverage_months"] = int(cf.get("income_coverage_months") or 12)
    return options


def get_income_bundle(client_user_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    S4: Call Plaid mock endpoints to fetch income data.
    Returns:
      {
        "payroll_resp": dict | None,
        "risk_resp": dict | None,
        "bank_resp": dict | None
      }
    Logic:
      - Always attempt payroll_income_get and payroll_risk_signals_get
      - If payroll missing/empty, fetch bank_income_get as fallback
    """
    opts = options or {}
    payroll_resp = plaid.payroll_income_get(client_user_id, options=opts)
    risk_resp = plaid.payroll_risk_signals_get(client_user_id, options=opts)

    bank_resp = None
    if not (isinstance(payroll_resp, dict) and payroll_resp.get("payroll_income")):
        bank_resp = plaid.bank_income_get(client_user_id, options=opts)

    return {
        "payroll_resp": payroll_resp,
        "risk_resp": risk_resp,
        "bank_resp": bank_resp,
    }
