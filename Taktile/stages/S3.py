from typing import Any, Dict

from Taktile.clients.experian import ExperianClient


experian = ExperianClient()


def build_experian_payload(intake: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the minimal Experian credit report payload from intake.
    Mirrors the payload assembled previously in the service orchestrator.
    """
    full_name = str(intake.get("user_fullname") or "").strip()
    parts = full_name.split()
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else (parts[0] if parts else "CONSUMER")
    scenario_val = ((intake.get("custom_fields") or {}).get("scenario"))

    payload: Dict[str, Any] = {
        "consumerPii": {
            "primaryApplicant": {
                "name": {"firstName": first, "lastName": last},
                "dob": {"dob": intake.get("user_dob")},
                "ssn": {"ssn": intake.get("ssn")},
                "currentAddress": {
                    "line1": intake.get("address_line1"),
                    "city": intake.get("address_city"),
                    "state": intake.get("address_state"),
                    "zipCode": intake.get("address_zip"),
                    "country": intake.get("user_country") or "US",
                },
            }
        },
        "permissiblePurpose": {"type": "CREDIT_GRANTING"},
        "addOns": {
            "riskModels": {"modelIndicator": ["V4", "FICO8"], "scorePercentile": "Y"},
            "summaries": {"summaryType": ["PROFILE"]},
            "ofac": "Y",
            "mla": "N",
            "scenario": scenario_val,
        },
    }
    return payload


def get_credit_report(intake: Dict[str, Any]) -> Dict[str, Any]:
    """
    S3: Build Experian payload and POST to Experian mock.
    Returns the ExperianClient envelope:
      {
        "status": int,
        "headers": dict,
        "data": dict   # creditProfile/errors, etc.
      }
    """
    payload = build_experian_payload(intake)
    return experian.post_credit_report(payload)
