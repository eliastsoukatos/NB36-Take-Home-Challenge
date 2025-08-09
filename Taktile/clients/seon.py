from typing import Any, Dict
import httpx
from Taktile.service.config import settings


class SeonClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = (base_url or settings.SEON_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.API_KEY_SEON
        self.client = httpx.Client(timeout=timeout)

    def aml_screen(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/SeonRestService/aml-api/v1"
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        resp = self.client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def fraud_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST {SEON_BASE_URL}/SeonRestService/fraud-api/v2
        Headers: X-API-KEY, Content-Type: application/json
        Payload example (fields are flexible for the mock):
        {
          "config": {
            "ip_api": true, "email_api": true, "phone_api": true, "device_fingerprinting": true,
            "email": {"version":"v3"}, "phone": {"version":"v2"},
            "ip": {"include":"flags,history,id","version":"v1"}
          },
          "ip": "...", "email": "...", "phone_number": "...",
          "user_fullname": "...", "user_dob": "YYYY-MM-DD", "user_country": "US",
          "session": "mock-session",
          "custom_fields": {"scenario": "pass|review|ko_fraud"}  // optional for demos
        }
        Returns SEON-like JSON with fraud_score, applied_rules, and detail blocks.
        """
        url = f"{self.base_url}/SeonRestService/fraud-api/v2"
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        resp = self.client.post(url, json=payload, headers=headers)
        # Do not raise; let policy handle non-2xx and error envelopes
        try:
            return resp.json()
        except Exception:
            return {"success": False, "error": {"code": "INVALID_JSON", "message": "Non-JSON response"}, "data": {}}
