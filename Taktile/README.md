# Taktile Orchestrator (T*)

This service simulates Taktile’s orchestration/policy layer. It owns all `T*` stages and calls external systems (SEON) directly. The backend (NB36) only does `B*` steps and delegates to this service.

Scope (AML-only demo):
- T1: Build AML payload from intake and call SEON AML API (no decision logic here)
- T2: Apply Compliance KO rules to SEON AML response (DECLINE vs PROCEED)
- Exposes a simple HTTP endpoint the backend can call

## Project layout

- service/
  - main.py (FastAPI app exposing `/workflows/kyc/aml-first`)
  - config.py (SEON_BASE_URL, API_KEY_SEON)
- stages/
  - T1.py (build payload + call SEON AML)
  - T2.py (KO rules: sanctions/PEP/crimelist → DECLINE; adverse media is context)
- clients/
  - seon.py (httpx client to SEON mock)
- runner/
  - orchestrate_aml.py (CLI runner to test T1+T2 without HTTP)
- docs/
  - aml_for_dummies.md (plain-English explainer)

## Requirements

- Python 3.10+
- fastapi, uvicorn, httpx, pydantic

Install:
- Option A (from repo root): `pip install -r Taktile/requirements.txt`
- Option B (from this folder): `cd Taktile && pip install -r requirements.txt`

## Configuration

- `SEON_BASE_URL` (default `http://localhost:8081`)
- `API_KEY_SEON` (default `secret` — must match SEON mock API key)

The SEON mock in this repo (`SEON_API`) expects header `X-API-KEY` equal to its configured `API_KEY` (default `secret`), and exposes the AML endpoint at:
```
POST {SEON_BASE_URL}/SeonRestService/aml-api/v1
```

## Run

Start the SEON mock first (example):
- From repo root: `python -m uvicorn SEON_API.app.main:app --reload --port 8081`

Start Taktile:
- From repo root: `python -m uvicorn Taktile.service.main:app --reload --port 9100`

## HTTP API (used by Backend)

- `POST /workflows/kyc/aml-first`
  - Body:
    ```
    {
      "case_id": "string",
      "intake": { ... }  // applicant intake (T1 builds AML payload from here)
    }
    ```
  - Response:
    ```
    {
      "case_id": "string",
      "decision": "DECLINE" | "PROCEED",
      "reasons": [ ... ],
      "details": { ... },
      "aml_raw": { ... } // raw SEON AML response
    }
    ```

## CLI Runner (no HTTP)

Run T1 + T2 directly for demos/tests (bypasses backend and HTTP):

- From repo root:
  - `python Taktile/runner/orchestrate_aml.py`
  - Or force scenarios supported by the SEON mock (e.g., `ko_compliance`):
    - `python Taktile/runner/orchestrate_aml.py ko_compliance`

Scenarios recognized by the SEON mock:
- `pass` → should `PROCEED`
- `review` → may still `PROCEED` (adverse media only considered as context)
- `ko_compliance` → should `DECLINE`
- `ko_fraud` → not used by AML-only; treated as `APPROVE` by mock, policy remains AML-focused

## Policy Summary

- AML is a legal/compliance “red light”:
  - Sanctions OR disqualifying PEP/Crimelist → DECLINE
  - Adverse media alone → context only (still PROCEED here)
  - Technical error/timeouts → DECLINE (technical decline) for this demo
- Tiers are not assigned at AML stage; they come later.
