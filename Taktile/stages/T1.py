from typing import Any, Dict

from Taktile.clients.seon import SeonClient


seon = SeonClient()


def build_aml_payload(intake: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the minimal AML payload expected by the SEON mock from the applicant intake.
    """
    payload: Dict[str, Any] = {
        "user_fullname": intake.get("user_fullname"),
        "user_dob": intake.get("user_dob"),
        "user_country": intake.get("user_country"),
        "email": intake.get("email"),
        "config": {
            "monitoring_required": False,
            "sources": {
                "sanction_enabled": True,
                "pep_enabled": True,
                "watchlist_enabled": True,
                "crimelist_enabled": True,
                "adversemedia_enabled": True,
            },
        },
        "custom_fields": intake.get("custom_fields") or {},
    }
    return payload


def run_aml_first(case_id: str, intake: Dict[str, Any]) -> Dict[str, Any]:
    """
    T1: Start KYC workflow (AML-first).
    - Build AML payload from intake
    - Call SEON AML API (no decision here)
    - Return raw AML response
    """
    aml_payload = build_aml_payload(intake)
    aml_response = seon.aml_screen(aml_payload)
    return {
        "case_id": case_id,
        "aml_raw": aml_response,
    }


def build_fraud_payload(intake: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a fraud payload for the SEON mock from the applicant intake.
    """
    payload: Dict[str, Any] = {
        "config": {
            "ip_api": True,
            "email_api": True,
            "phone_api": True,
            "device_fingerprinting": True,
            "email": {"version": "v3"},
            "phone": {"version": "v2"},
            "ip": {"include": "flags,history,id", "version": "v1"},
        },
        "ip": intake.get("ip"),
        "email": intake.get("email"),
        "phone_number": intake.get("phone_number"),
        "user_fullname": intake.get("user_fullname"),
        "user_dob": intake.get("user_dob"),
        "user_country": intake.get("user_country"),
        "session": intake.get("session") or "mock-session",
        "custom_fields": intake.get("custom_fields") or {},
    }
    return payload


def run_fraud(case_id: str, intake: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build payload and call SEON Fraud API, returning the raw response.
    """
    fraud_payload = build_fraud_payload(intake)
    fraud_response = seon.fraud_check(fraud_payload)
    return {
        "case_id": case_id,
        "fraud_raw": fraud_response,
    }
