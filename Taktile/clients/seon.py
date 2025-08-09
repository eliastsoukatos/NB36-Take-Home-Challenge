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
