# Mock Experian US Credit Profile v2 (Demo Service)

This is a lightweight FastAPI service that simulates Experian's Credit Profile API for demos and testing. It returns realistic payloads, supports scenario forcing, and basic vendor error simulations.

Key features
- Single endpoint: POST /v2/credit-report
- Scenario control via request.addOns.scenario:
  - pass → clean profile, high score, CREDIT_PASS
  - review_credit → missing risk model + disputed tradeline, CREDIT_REVIEW
  - ko_credit → OFAC hit, CREDIT_DECLINE
- Error simulations via lastName: FAIL_400, FAIL_403, FAIL_404, FAIL_500, TIMEOUT

## Run locally

Prereqs
- Python 3.10+
- pip install fastapi uvicorn pydantic

Start server (port 8000)
- From repo root:
  - python -m uvicorn Experian_API.app.main:app --reload --port 8000

Health
- GET http://localhost:8000/ → {"status":"ok","service":"mock-experian-credit-profile"}

## Request and headers

Endpoint
- POST http://localhost:8000/v2/credit-report

Required headers
- Authorization: Bearer sandbox-token
- clientReferenceId: SBMYSQL
- Accept: application/json
- Content-Type: application/json

Minimal request body (example)
{
  "consumerPii": {
    "primaryApplicant": {
      "name": { "firstName": "JON", "lastName": "CONSUMER" },
      "dob": { "dob": "1991-01-01" },           // ISO (YYYY-MM-DD)
      "ssn": { "ssn": "123-45-6789" },
      "currentAddress": { "line1": "1475 MAIN ST", "city": "ANYTOWN", "state": "WA", "zipCode": "12345", "country": "US" }
    }
  },
  "addOns": {
    "riskModels": { "modelIndicator": ["V4","FICO8"], "scorePercentile": "Y" },
    "summaries": { "summaryType": ["PROFILE"] },

    // Scenario control for demos (optional):
    // "scenario": "pass" | "review_credit" | "ko_credit"
    "scenario": "pass"
  }
}

Notes
- You can also force vendor errors by setting lastName to FAIL_400, FAIL_403, FAIL_404, FAIL_500, or TIMEOUT.

## Scenarios

Use addOns.scenario in the request body:

- pass
  - Clears severe fraud flags, clears OFAC, raises score → CREDIT_PASS
- review_credit
  - Removes risk model and flags a disputed tradeline → CREDIT_REVIEW
- ko_credit
  - Forces OFAC match → CREDIT_DECLINE

Error simulations (via lastName):
- "FAIL_400" → 400 Bad Request
- "FAIL_403" → 403 Forbidden
- "FAIL_404" → 404 Not Found
- "FAIL_500" → 500 Server Error
- "TIMEOUT" → ~12s delay then 504 Gateway Timeout

## Typical response shape (success)

{
  "creditProfile": [
    {
      "riskModel": [ { "modelIndicator": "V4", "score": "690", ... } ],
      "ofac": { "messageText": "" },
      "fraudShield": [ { "fraudShieldIndicators": { "indicator": [] } } ],
      "tradeline": [ ... ],
      "inquiry": [ ... ],
      "statement": [ ... ],
      ...
    }
  ],
  "dataSource": { "dataSourceResponse": "BUREAU" },
  ...
}

When combined with the Taktile policy (T5), the service outputs will be evaluated to:
- CREDIT_PASS (with bureau_tier and final_tier = min(fraudTier, bureauTier))
- CREDIT_REVIEW (review_reasons provided)
- CREDIT_DECLINE (ko_reasons provided)

## cURL examples

Success (pass)
curl -X POST http://localhost:8000/v2/credit-report \
  -H "Authorization: Bearer sandbox-token" \
  -H "clientReferenceId: SBMYSQL" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "consumerPii": {
      "primaryApplicant": {
        "name": { "firstName": "JON", "lastName": "CONSUMER" },
        "dob": { "dob": "1991-01-01" },
        "ssn": { "ssn": "123-45-6789" },
        "currentAddress": { "line1": "1475 MAIN ST", "city": "ANYTOWN", "state": "WA", "zipCode": "12345", "country": "US" }
      }
    },
    "addOns": {
      "riskModels": { "modelIndicator": ["V4","FICO8"], "scorePercentile": "Y" },
      "summaries": { "summaryType": ["PROFILE"] },
      "scenario": "pass"
    }
  }'

Credit review
- Use "review_credit" as scenario.

Credit decline
- Use "ko_credit" as scenario.

Vendor error
- Set lastName to "FAIL_500" in the request to return HTTP 500 with an error body.
- Set lastName to "TIMEOUT" to simulate delay then 504.

## Integration notes

- Taktile/service/config.py uses:
  - EXPERIAN_BASE_URL (default http://localhost:8000)
  - EXPERIAN_TOKEN (default sandbox-token)
  - EXPERIAN_CLIENT_REF (default SBMYSQL)
- Taktile service calls this API over HTTP; renaming the folder won’t impact imports.
- The demo frontend posts to the NB36 backend, which calls Taktile → SEON → (if pass) → Experian → then returns decision and tiers to the UI.
