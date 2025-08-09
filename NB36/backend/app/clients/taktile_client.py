from typing import Any, Dict
import httpx
from ..config import settings


class TaktileClient:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = (base_url or settings.TAKTILE_BASE_URL).rstrip("/")
        self.client = httpx.Client(timeout=timeout)

    def aml_first(self, case_id: str, intake: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls Taktile orchestrator to run AML-first workflow.
        Expects response:
          {
            "decision": "DECLINE" | "PROCEED",
            "reasons": [ ... ],
            "details": { ... },
            "aml_raw": { ... }
          }
        """
        url = f"{self.base_url}/workflows/kyc/aml-first"
        payload = {"case_id": case_id, "intake": intake}
        resp = self.client.post(url, json=payload, headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        return resp.json()

    def kyc_full(self, case_id: str, intake: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls Taktile orchestrator to run full KYC (AML + Fraud).
        Expects response:
          {
            "case_id": ...,
            "status": "AML_DECLINE" | "FRAUD_DECLINE" | "FRAUD_REVIEW" | "FRAUD_PASS",
            "aml_decision": {...} | null,
            "fraud_decision": {...} | null,
            "provisional_tier": int | null,
            "aml_raw": {...} | null,
            "fraud_raw": {...} | null
          }
        """
        url = f"{self.base_url}/workflows/kyc/full"
        payload = {"case_id": case_id, "intake": intake}
        resp = self.client.post(url, json=payload, headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        return resp.json()
