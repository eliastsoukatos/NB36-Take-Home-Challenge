from typing import Any, Dict, Optional
import httpx
from Taktile.service.config import settings


class PlaidClient:
    """
    Thin HTTP client for the Plaid mock (Income) service.
    Defaults to PLAID_BASE_URL=http://localhost:8200
    """

    def __init__(self, base_url: Optional[str] = None, timeout_seconds: Optional[float] = None) -> None:
        self.base_url = (base_url or settings.PLAID_BASE_URL).rstrip("/")
        self.timeout = timeout_seconds or settings.PLAID_TIMEOUT_SECONDS
        self.client = httpx.Client(timeout=self.timeout)

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        # Plaid-style: return JSON body, do not raise on non-2xx; mock always 200 anyway
        try:
            r = self.client.post(url, json=payload, headers={"Content-Type": "application/json"})
            return r.json()
        except Exception as e:
            # Model an error body
            return {
                "error_type": "API_ERROR",
                "error_code": "REQUEST_EXCEPTION",
                "display_message": str(e),
                "request_id": "req-exception",
            }

    # Minimal endpoints used by the income stage

    def payroll_income_get(self, client_user_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "client_user_id": client_user_id,
            "client_id": "sandbox",
            "secret": "sandbox",
        }
        if options:
            payload["options"] = options
        return self._post_json("/credit/payroll_income/get", payload)

    def payroll_risk_signals_get(self, client_user_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "client_user_id": client_user_id,
            "client_id": "sandbox",
            "secret": "sandbox",
        }
        if options:
            payload["options"] = options
        return self._post_json("/credit/payroll_income/risk_signals/get", payload)

    def bank_income_get(self, client_user_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "client_user_id": client_user_id,
            "client_id": "sandbox",
            "secret": "sandbox",
        }
        if options:
            payload["options"] = options
        return self._post_json("/credit/bank_income/get", payload)

    def employment_get(self, client_user_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "client_user_id": client_user_id,
            "client_id": "sandbox",
            "secret": "sandbox",
        }
        if options:
            payload["options"] = options
        return self._post_json("/credit/employment/get", payload)

    # Optional: PDF get (not strictly required for decisioning flow)
    def bank_income_pdf_get(self, client_user_id: str, options: Optional[Dict[str, Any]] = None) -> bytes:
        # For now: return empty bytes; can be implemented if needed in UI
        return b""
