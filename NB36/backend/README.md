# NB36 Backend (B*) — Minimal API that delegates orchestration to Taktile

This service owns only the Backend “B*” steps. For this demo:
- B1: Create case (in-memory)
- Delegates orchestration to Taktile (T*) which calls SEON and decides AML outcome.
- Exposes simple HTTP endpoints for intake and case retrieval.

## Endpoints

- POST /apply/aml-first
  - Body: Applicant intake JSON (see example below)
  - Flow:
    1) B1 creates a case (returns case_id)
    2) Backend calls Taktile /workflows/kyc/aml-first with {case_id, intake}
    3) Taktile calls SEON AML, applies KO rules, and returns a decision
    4) Backend persists aml_raw + aml_decision on the case and returns the decision
- GET /cases/{case_id}
  - Returns the stored case with timeline and aml_decision (if present)

## Project layout

- app/
  - main.py (FastAPI app + endpoints)
  - config.py (TAKTILE_BASE_URL)
  - stages/
    - B1.py (create/get/update case in memory)
  - clients/
    - taktile_client.py (HTTP client to call Taktile)

## Requirements

- Python 3.10+
- fastapi, uvicorn, httpx, pydantic

Install:
- Option A (rooted path): pip install -r NB36/backend/requirements.txt
- Option B (from this folder): cd NB36/backend && pip install -r requirements.txt

## Configuration

- TAKTILE_BASE_URL (default http://localhost:9100)

## Run

Start the Taktile service first (see Taktile/README.md), then run the backend:

From repo root:
- python -m uvicorn NB36.backend.app.main:app --reload --port 9000

Or from NB36/backend directory:
- uvicorn app.main:app --reload --port 9000

## Example

1) Start SEON mock (port 8081), then Taktile (port 9100), then Backend (port 9000).

2) Create an application and run AML-first:

curl -X POST http://localhost:9000/apply/aml-first ^
  -H "Content-Type: application/json" ^
  -d "{
    \"user_fullname\": \"Alice Smith\",
    \"user_dob\": \"1995-01-01\",
    \"user_country\": \"US\",
    \"ssn\": \"123-45-6789\",
    \"gov_id_type\": \"DL\",
    \"gov_id_number\": \"A1234567\",
    \"address_line1\": \"123 Main St\",
    \"address_city\": \"Austin\",
    \"address_state\": \"TX\",
    \"address_zip\": \"78701\",
    \"email\": \"alice@good.com\",
    \"phone_number\": \"+14155550123\",
    \"custom_fields\": {\"scenario\": \"pass\"}
  }"

- Change custom_fields.scenario to "ko_compliance" to force a DECLINE from Taktile (via SEON mock).

3) Fetch the case:

curl http://localhost:9000/cases/{case_id}
