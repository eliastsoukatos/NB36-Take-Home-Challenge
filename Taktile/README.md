# Taktile Orchestrator (T*)

This service simulates Taktile’s orchestration/policy layer. It owns all `T*` stages and calls external systems (SEON) directly. The backend (NB36) only does `B*` steps and delegates to this service.

Scope (AML + Fraud demo)
- T1: Build AML payload from intake and call SEON AML API (no decision logic here)
- T2: Apply Compliance KO rules to SEON AML response (DECLINE vs PROCEED)
- S2: Call SEON Fraud API (device, IP, email, phone, session signals)
- T4: Evaluate fraud response (FRAUD_DECLINE | FRAUD_REVIEW | FRAUD_PASS) and derive provisional tier (T5)

## Project layout

- service/
  - main.py (FastAPI app exposing `/workflows/kyc/aml-first` and `/workflows/kyc/full`)
  - config.py (SEON_BASE_URL, API_KEY_SEON)
- stages/
  - T1.py (build payloads + call SEON AML/Fraud)
  - T2.py (AML KO rules: sanctions/PEP/crimelist → DECLINE; adverse media is context)
  - T4.py (Fraud rules: score thresholds + severe flags; map score → provisional tier)
- clients/
  - seon.py (httpx client to SEON mock; aml_screen + fraud_check)
- runner/
  - orchestrate_aml.py (CLI runner to test T1+T2 without HTTP)
  - orchestrate_full_kyc.py (CLI runner to test full KYC AML+Fraud via HTTP)
- docs/
  - aml_for_dummies.md (plain-English explainer)
  - fraud_policy_for_dummies.md (plain-English explainer)

## Requirements

- Python 3.10+
- fastapi, uvicorn, httpx, pydantic

Install:
- Option A (from repo root): `pip install -r Taktile/requirements.txt`
- Option B (from this folder): `cd Taktile && pip install -r requirements.txt`

## Configuration

- `SEON_BASE_URL` (default `http://localhost:8081`)
- `API_KEY_SEON` (default `secret` — must match SEON mock API key)

The SEON mock in this repo (`SEON_API`) expects header `X-API-KEY` equal to its configured `API_KEY` (default `secret`) and exposes:
```
POST {SEON_BASE_URL}/SeonRestService/aml-api/v1
POST {SEON_BASE_URL}/SeonRestService/fraud-api/v2
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

- `POST /workflows/kyc/full`
  - Body:
    ```
    {
      "case_id": "string",
      "intake": {
        "user_fullname": "string",
        "user_dob": "YYYY-MM-DD",
        "user_country": "US",
        "ssn": "string",
        "gov_id_type": "DL|PASSPORT|STATE_ID",
        "gov_id_number": "string",
        "address_line1": "string",
        "address_city": "string",
        "address_state": "string",
        "address_zip": "string",
        "email": "string",
        "phone_number": "string",
        "ip": "string (optional)",
        "session": "string (optional)",
        "custom_fields": { "scenario": "pass|review|ko_fraud|ko_compliance" } // optional
      }
    }
    ```
  - Response:
    ```
    {
      "case_id": "uuid",
      "status": "AML_DECLINE | FRAUD_DECLINE | FRAUD_REVIEW | FRAUD_PASS",
      "aml_decision": { "decision": "DECLINE|PROCEED", "reasons": [ ... ], "details": { ... } },
      "fraud_decision": { "decision": "FRAUD_DECLINE|FRAUD_REVIEW|FRAUD_PASS", "provisional_tier": 0-7|null, "reasons": [ ... ], "details": {"fraud_score": float} },
      "provisional_tier": 0-7 | null,
      "aml_raw": { ... },
      "fraud_raw": { ... }
    }
    ```

## CLI Runners (no backend required)

Run via HTTP to Taktile (full KYC):
- From repo root:
  - `python Taktile/runner/orchestrate_full_kyc.py`
  - Or force scenarios supported by the SEON mock:
    - `python Taktile/runner/orchestrate_full_kyc.py ko_compliance` (AML DECLINE)
    - `python Taktile/runner/orchestrate_full_kyc.py ko_fraud` (Fraud DECISION path)
    - `python Taktile/runner/orchestrate_full_kyc.py pass` (PROCEED + tier)
    - `python Taktile/runner/orchestrate_full_kyc.py review` (Fraud REVIEW)

Run AML-only policy without HTTP:
- From repo root:
  - `python Taktile/runner/orchestrate_aml.py`
  - Or force scenarios:
    - `python Taktile/runner/orchestrate_aml.py ko_compliance`

## Policy Summary

- AML is a legal/compliance “red light”:
  - Sanctions OR disqualifying PEP/Crimelist → DECLINE
  - Adverse media alone → context only (still PROCEED here)
  - Technical error/timeouts → DECLINE (technical decline) for this demo
- Fraud focuses on session/device/network trustworthiness:
  - Very high risk score or multiple severe flags → FRAUD_DECLINE
  - Medium-high risk or single severe flag or missing device/session → FRAUD_REVIEW
  - Clean signals/low score → FRAUD_PASS with provisional tier (7 best → 0 base)
