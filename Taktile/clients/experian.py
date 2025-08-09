from typing import Any, Dict
import httpx
from Taktile.service.config import settings


class ExperianClient:
    def __init__(self, base_url: str | None = None, token: str | None = None, client_ref: str | None = None, timeout_seconds: float | None = None) -> None:
        self.base_url = (base_url or settings.EXPERIAN_BASE_URL).rstrip("/")
        self.token = token or settings.EXPERIAN_TOKEN
        self.client_ref = client_ref or settings.EXPERIAN_CLIENT_REF
        self.timeout = timeout_seconds or settings.EXPERIAN_TIMEOUT_SECONDS
        self.client = httpx.Client(timeout=self.timeout)

    def post_credit_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST {EXPERIAN_BASE_URL}/v2/credit-report
        Headers:
          - Authorization: Bearer <token>
          - clientReferenceId: <client_ref>
          - Accept: application/json
          - Content-Type: application/json
        Returns JSON; on non-JSON, returns an error envelope.
        """
        url = f"{self.base_url}/v2/credit-report"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "clientReferenceId": self.client_ref,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        try:
            resp = self.client.post(url, json=payload, headers=headers)
            # Do not raise; policy should interpret vendor errors/status
            try:
                body = resp.json()
            except Exception:
                body = {"creditProfile": [], "errors": [{"code": "INVALID_JSON", "message": "Non-JSON response", "status": str(resp.status_code)}]}
            return {
                "status": resp.status_code,
                "headers": dict(resp.headers),
                "data": body,
            }
        except Exception as e:
            # Surface as synthetic timeout/vendor error
            return {
                "status": 0,
                "headers": {},
                "data": {
                    "creditProfile": [],
                    "errors": [{"code": "REQUEST_EXCEPTION", "message": str(e), "status": "0"}],
                },
            }
