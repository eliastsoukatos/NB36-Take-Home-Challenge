import json
import sys
from typing import Any, Dict

from Taktile.stages.T1 import run_aml_first
from Taktile.stages.T2 import evaluate_aml


def example_intake(scenario: str | None = None) -> Dict[str, Any]:
    """
    Build an example intake payload. You can edit values or pass a scenario to drive the SEON mock.
    Known scenarios in SEON_API mock: pass, review, ko_fraud, ko_compliance
    """
    intake = {
        "user_fullname": "Bob Jones",
        "user_dob": "1990-05-05",
        "user_country": "US",
        "ssn": "111-22-3333",
        "gov_id_type": "DL",
        "gov_id_number": "X999000",
        "address_line1": "55 Broadway",
        "address_city": "NYC",
        "address_state": "NY",
        "address_zip": "10006",
        "email": "bob@sanction.com",
        "phone_number": "+12125551234",
        "custom_fields": {},
    }
    if scenario:
        intake["custom_fields"]["scenario"] = scenario
    return intake


def main():
    # Optional CLI arg: scenario (e.g., python orchestrate_aml.py ko_compliance)
    scenario = sys.argv[1] if len(sys.argv) > 1 else None
    case_id = "demo-case-001"  # this CLI runs T1/T2 directly without creating a backend case

    intake = example_intake(scenario=scenario)

    # T1: build AML payload + call SEON mock
    t1 = run_aml_first(case_id=case_id, intake=intake)
    aml_raw = t1.get("aml_raw")

    # T2: compliance KO logic
    decision = evaluate_aml(aml_raw)

    result = {
        "case_id": case_id,
        "aml_decision": decision,
        "aml_raw_present": isinstance(aml_raw, dict),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
