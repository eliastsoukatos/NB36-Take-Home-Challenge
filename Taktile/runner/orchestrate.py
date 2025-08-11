import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

# Default base URL for the Taktile service
#DEFAULT_BASE = "https://nb-taktile.onrender.com"
DEFAULT_BASE = "http://localhost:9100"


def post_json(url: str, payload: Dict[str, Any], timeout: float = 10.0) -> tuple[int, Dict[str, Any] | str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except Exception:
                return resp.status, body
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
            return e.code, json.loads(body)
        except Exception:
            return e.code, str(e)
    except Exception as e:
        return 0, f"Request error: {e}"


def example_intake_full(scenario: Optional[str] = None, income_opts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build an example intake payload for Full KYC (AML + Fraud + Credit + Income).
    """
    intake = {
        "user_fullname": "Alice Smith",
        "user_dob": "1995-01-01",
        "user_country": "US",
        "ssn": "123-45-6789",
        "gov_id_type": "DL",
        "gov_id_number": "A1234567",
        "address_line1": "123 Main St",
        "address_city": "Austin",
        "address_state": "TX",
        "address_zip": "78701",
        "email": "alice@good.com",
        "phone_number": "+14155550123",
        "ip": "1.2.3.4",
        "session": "mock-session",
        "custom_fields": {},
    }
    if scenario:
        intake["custom_fields"]["scenario"] = scenario

    if income_opts:
        # Pass-through keys understood by the service S4 builder
        if "income_force_mode" in income_opts:
            intake["custom_fields"]["income_force_mode"] = income_opts["income_force_mode"]
        if "income_risk_profile" in income_opts:
            intake["custom_fields"]["income_risk_profile"] = income_opts["income_risk_profile"]
        if "income_inject_error" in income_opts:
            intake["custom_fields"]["income_inject_error"] = income_opts["income_inject_error"]
        if "income_coverage_months" in income_opts:
            intake["custom_fields"]["income_coverage_months"] = income_opts["income_coverage_months"]

    return intake


def run_full(base: str, case_id: str, scenario: Optional[str], income_opts: Optional[Dict[str, Any]], pretty: bool) -> None:
    intake = example_intake_full(scenario=scenario, income_opts=income_opts)
    status, resp = post_json(
        f"{base}/workflows/kyc/full",
        {"case_id": case_id, "intake": intake},
    )
    out = {"mode": "full", "http_status": status, "response": resp}
    print(json.dumps(out, indent=2 if pretty else None))


def run_suite(base: str, pretty: bool) -> None:
    scenarios = ["pass", "review", "ko_fraud", "ko_compliance"]
    for sc in scenarios:
        run_full(base, f"suite-full-{sc}", sc, {}, pretty)

    # Income variations
    run_full(base, "suite-full-income-payroll", "pass", {"income_force_mode": "payroll"}, pretty)
    run_full(base, "suite-full-income-bank-thin", "pass", {"income_force_mode": "bank", "income_coverage_months": 2}, pretty)
    run_full(base, "suite-full-income-error", "pass", {"income_inject_error": True}, pretty)


def main() -> None:
    parser = argparse.ArgumentParser(prog="orchestrate", description="Run Full KYC scenarios against the Taktile service")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_full = sub.add_parser("full", help="Run full KYC flow (AML → Fraud → Credit → Income)")
    p_full.add_argument("--base", default=DEFAULT_BASE, help="Taktile base URL")
    p_full.add_argument("--case-id", default="demo-full-001", help="Case ID to use")
    p_full.add_argument("--scenario", default="pass", help="SEON scenario: pass|review|ko_fraud|ko_compliance")
    p_full.add_argument("--income-force-mode", choices=["payroll", "bank", "none"], help="Force Plaid mode")
    p_full.add_argument("--income-risk-profile", help="Plaid risk profile e.g. NO_FINDINGS|MEDIUM|HIGH")
    p_full.add_argument("--income-inject-error", action="store_true", help="Inject a Plaid error for testing")
    p_full.add_argument("--coverage-months", type=int, default=12, help="Requested coverage months (bank fallback rule)")
    p_full.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    p_suite = sub.add_parser("suite", help="Run a suite of scenarios across Full flow")
    p_suite.add_argument("--base", default=DEFAULT_BASE, help="Taktile base URL")
    p_suite.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    if args.cmd == "full":
        opts: Dict[str, Any] = {}
        if args.income_force_mode and args.income_force_mode != "none":
            opts["income_force_mode"] = args.income_force_mode
        if args.income_risk_profile:
            opts["income_risk_profile"] = args.income_risk_profile
        if args.income_inject_error:
            opts["income_inject_error"] = True
        if args.coverage_months is not None:
            opts["income_coverage_months"] = args.coverage_months
        run_full(args.base, args.case_id, args.scenario, opts, args.pretty)
    elif args.cmd == "suite":
        run_suite(args.base, args.pretty)
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
