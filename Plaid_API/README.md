# Mock Plaid Income API (FastAPI)

A lightweight mock of Plaid’s Income flows for demos/tests. Implements Payroll Income first, Bank Income fallback, risk signals, employment, webhooks, and a PDF report — all without real Plaid credentials.

Tech
- Python 3.11
- FastAPI + Uvicorn
- Pydantic
- httpx (for webhook POSTs)
- reportlab (for PDF)

## Install and run

From repo root (Plaid on 8200; Experian remains on 8000):

- Install deps:
  pip install -r Plaid_API/requirements.txt

- Run:
  uvicorn Plaid_API.main:app --reload --port 8200

- Health:
  curl -s http://localhost:8200/ | jq

Default auth behavior:
- Provide either headers PLAID-CLIENT-ID / PLAID-SECRET or JSON body client_id / secret
- If envs PLAID_CLIENT_ID / PLAID_SECRET are set, values must match; otherwise any non-empty strings are accepted
- Errors are returned as Plaid-style JSON with HTTP 200:
  {
    "error_type": "INVALID_INPUT",
    "error_code": "INVALID_CREDENTIALS",
    "display_message": "...",
    "request_id": "..."
  }

## Endpoints (POST unless noted)

- /user/create
- /link/token/create
- /item/public_token/exchange
- /credit/sessions/get
- /credit/payroll_income/get
- /credit/payroll_income/risk_signals/get
- /credit/bank_income/get
- /credit/bank_income/pdf/get (application/pdf)
- /credit/bank_income/refresh
- /credit/employment/get
- /webhooks/plaid-income (receiver)
- /sandbox/income/fire_webhook (simulate sending a webhook)
- GET / (health)

Options/toggles (in body or options object)
- force_mode: "payroll" | "bank" | "document" | "empty"
  - payroll: ensure payroll income is present
  - bank: ensure bank income is present
  - empty: return no data for the product
- coverage_months: 1–60 (default 12) influences bank coverage FULL vs PARTIAL
- risk_profile: "clean" | "suspicious" influences risk signals
- inject_error: e.g., "ITEM_LOGIN_REQUIRED", "RATE_LIMIT_EXCEEDED" returns Plaid-style error JSON with HTTP 200

Deterministic data
- Randomness is seeded by client_user_id so the same user yields the same employer, cadence, and income numbers across runs.

## Example curl calls (6+)

1) Create a user
curl -s -X POST http://localhost:8200/user/create \
  -H "Content-Type: application/json" \
  -d '{ "client_user_id": "user-123", "client_id": "x", "secret": "y" }' | jq

2) Create a link token
curl -s -X POST http://localhost:8200/link/token/create \
  -H "Content-Type: application/json" \
  -d '{
    "client_name":"Demo",
    "language":"en",
    "country_codes":["US"],
    "user":{"client_user_id":"user-123"},
    "products":["income_verification"],
    "webhook":"http://localhost:8200/webhooks/plaid-income",
    "client_id":"x","secret":"y"
  }' | jq

3) Exchange public_token for access_token
curl -s -X POST http://localhost:8200/item/public_token/exchange \
  -H "Content-Type: application/json" \
  -d '{ "public_token":"public-sandbox-abc", "client_user_id":"user-123", "client_id":"x", "secret":"y" }' | jq

4) Get payroll income (force payroll)
curl -s -X POST http://localhost:8200/credit/payroll_income/get \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "ACCESS_TOKEN_FROM_EXCHANGE",
    "options": { "force_mode": "payroll" },
    "client_id":"x","secret":"y"
  }' | jq

5) Get bank income (12 months default)
curl -s -X POST http://localhost:8200/credit/bank_income/get \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "ACCESS_TOKEN_FROM_EXCHANGE",
    "options": { "coverage_months": 12 },
    "client_id":"x","secret":"y"
  }' | jq

6) Download bank income PDF
curl -X POST http://localhost:8200/credit/bank_income/pdf/get \
  -H "Content-Type: application/json" \
  -o bank_income.pdf \
  -d '{ "access_token": "ACCESS_TOKEN_FROM_EXCHANGE", "client_id":"x","secret":"y" }' && echo "Saved bank_income.pdf"

7) Risk signals (suspicious)
curl -s -X POST http://localhost:8200/credit/payroll_income/risk_signals/get \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "ACCESS_TOKEN_FROM_EXCHANGE",
    "options": { "risk_profile":"suspicious" },
    "client_id":"x","secret":"y"
  }' | jq

8) Fire webhook to your app
curl -s -X POST http://localhost:8200/sandbox/income/fire_webhook \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_code":"INCOME_VERIFICATION",
    "item_id":"ITEM_ID_FROM_EXCHANGE",
    "target":"http://localhost:8200/webhooks/plaid-income",
    "client_id":"x","secret":"y"
  }' | jq

9) Inject an error (Plaid-style JSON, HTTP 200)
curl -s -X POST http://localhost:8200/credit/bank_income/get \
  -H "Content-Type: application/json" \
  -d '{
    "access_token":"ACCESS_TOKEN_FROM_EXCHANGE",
    "options":{"inject_error":"RATE_LIMIT_EXCEEDED"},
    "client_id":"x","secret":"y"
  }' | jq

## Response shape examples

Payroll Income
{
  "payroll_income": {
    "employer": "Acme Corp",
    "pay_frequency": "BIWEEKLY",
    "ytd_gross": 45210.18,
    "streams": [
      { "label": "Primary job", "cadence": "BIWEEKLY", "gross": 2500.00, "net": 1900.00 }
    ]
  },
  "request_id": "..."
}

Bank Income
{
  "bank_income": {
    "coverage": "FULL",
    "streams": [
      { "source": "Direct deposit", "cadence": "BIWEEKLY", "average_net": 1850.42, "confidence": "HIGH" }
    ]
  },
  "request_id": "..."
}

Credit session meta
{
  "session_id": "sess-abc123",
  "echo": { ... your input ... },
  "results": { "status":"ok", "force_mode":"payroll" },
  "request_id": "..."
}

## Notes

- HTTP status is 200 for both success and errors (Plaid style), except the PDF endpoint returns application/pdf.
- Every response includes request_id (uuid4).
- Logs include method, path, and request_id.
- Data is deterministic per client_user_id; use the same id for stable results across runs.

## License

Demo/mock use only.
