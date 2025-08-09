from typing import Any, Dict, List


class ComplianceDecision:
    DECLINE = "DECLINE"
    PROCEED = "PROCEED"


def evaluate_aml(aml_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate AML response (from SEON mock) and return a decision dict.

    Expected aml_response shape:
      {
        "success": bool,
        "error": {...} | {},
        "data": {
          "has_watchlist_match": bool,
          "has_sanction_match": bool,
          "has_crimelist_match": bool,
          "has_pep_match": bool,
          "has_adversemedia_match": bool,
          "result_payload": {...}
        }
      }
    """
    if not aml_response or not aml_response.get("success"):
        return {
            "decision": ComplianceDecision.DECLINE,
            "reasons": ["technical_error_or_timeout"],
            "details": aml_response.get("error") if isinstance(aml_response, dict) else {},
        }

    data = aml_response.get("data") or {}
    reasons: List[str] = []

    if data.get("has_sanction_match"):
        reasons.append("sanctions_match")
    if data.get("has_pep_match"):
        reasons.append("pep_match")
    if data.get("has_crimelist_match"):
        reasons.append("crimelist_match")
    if data.get("has_adversemedia_match"):
        reasons.append("adverse_media_signal")

    if any(r in reasons for r in ("sanctions_match", "pep_match", "crimelist_match")):
        return {
            "decision": ComplianceDecision.DECLINE,
            "reasons": reasons,
            "details": {"source": "aml_screening"},
        }

    return {
        "decision": ComplianceDecision.PROCEED,
        "reasons": reasons,
        "details": {"source": "aml_screening"},
    }
