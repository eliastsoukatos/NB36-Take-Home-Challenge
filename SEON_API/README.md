# SEON Mock Service (FastAPI)

Production-like mock of SEON APIs used during KYC, with deterministic responses, X-API-KEY auth, signed webhooks (HMAC-SHA256), and in-memory stores for lists, labels, and self-exclusion.

## Tech

- Python 3.11+
- FastAPI, Uvicorn
- Pydantic v2
- httpx for webhook POSTs
- Deterministic generators seeded by input
- CORS enabled for localhost
- Structured request logs with X-Request-ID

## Endpoints

- Fraud API v2: POST /SeonRestService/fraud-api/v2
- AML API v1: POST /SeonRestService/aml-api/v1
- Lists API:
  - PUT /SeonRestService/fraud-api/state-field/v1/
  - GET /SeonRestService/fraud-api/state-field/v1/entries
- Label API: PUT /SeonRestService/fraud-api/transaction-label/v2
- Self Exclusion:
  - PUT /SeonRestService/fraud-api/exclude/v1
  - DELETE /SeonRestService/fraud-api/exclude/v1
  - GET /SeonRestService/fraud-api/exclude/v1
- Debug: GET /__debug/webhook-attempts
- Health: GET /__health

## Auth

- All API routes (except /__health and /__debug/*) require header: `X-API-KEY: <value>`
- 401 if missing/invalid
- Error envelope:
  ```
  { "success": false, "error": { "code": "AUTH_MISSING_KEY|AUTH_INVALID_KEY", "message": "..." } }
  ```

## Environment Variables

- `API_KEY` (required to protect endpoints) default: `secret`
- `SECRET_KEY` (HMAC signing for webhooks) default: `devsecret`
- `WEBHOOK_URL` (optional) if set and request has `custom_fields.emit_webhooks=true`, a webhook is sent
- `PORT` (optional) default: 8080

Example:
```
API_KEY=secret
WEBHOOK_URL=http://localhost:9000/hook
SECRET_KEY=devsecret
```

## Install & Run

Install dependencies (in venv):

```
pip install -r requirements.txt
```

Run dev server:

```
uvicorn app.main:app --reload --port 8080
```

Docker:

```
docker build -t seon-mock:latest .
docker run --rm -p 8080:8080 -e API_KEY=secret -e SECRET_KEY=devsecret -e WEBHOOK_URL= http://localhost:8080
```

Makefile targets (optional, if make is available):

- `make install` - pip install
- `make run` - uvicorn with reload
- `make docker-build`
- `make docker-run` (exposes port 8080)

## Scenarios

- Preferred: `custom_fields.scenario` enum: `pass` | `review` | `ko_fraud` | `ko_compliance`
- Fallback by email domain suffix:
  - `@good.com` → pass
  - `@maybe.com` → review
  - `@fraud.com` → ko_fraud
  - `@sanction.com` → ko_compliance
- Fraud mapping:
  - pass → APPROVE, fraud_score ~ 15–35
  - review → REVIEW, fraud_score ~ 70–85, include VOIP/new domain/geo mismatch
  - ko_fraud → DECLINE, fraud_score ~ 90–98, VPN/proxy, device farm hints
  - ko_compliance → DECLINE, fraud_score ~ 90–98, aml-like flags inside applied_rules
- AML mapping:
  - pass → all false
  - review → `has_adversemedia_match=true` with a small array
  - ko_compliance → `has_sanction_match=true` (optionally PEP/watchlist), with sample list entries
  - ko_fraud → treated as pass here

## Example cURL

PASS:
```
curl -X POST 'http://localhost:8080/SeonRestService/fraud-api/v2' \
  -H 'X-API-KEY: secret' -H 'Content-Type: application/json' \
  -d '{
    "email":"alice@good.com",
    "phone_number":"+14155550123",
    "ip":"1.2.3.4",
    "user_fullname":"Alice Smith",
    "user_dob":"1995-01-01",
    "user_country":"US",
    "session":"mock-session",
    "custom_fields": {"scenario":"pass","emit_webhooks":true}
  }'
```

REVIEW:
```
curl -X POST 'http://localhost:8080/SeonRestService/fraud-api/v2' \
  -H 'X-API-KEY: secret' -H 'Content-Type: application/json' \
  -d '{"email":"bob@maybe.com","phone_number":"+14155550124","ip":"5.6.7.8","user_fullname":"Bob Jones","user_dob":"1990-05-05","user_country":"US","session":"mock-session"}'
```

KO FRAUD:
```
curl -X POST 'http://localhost:8080/SeonRestService/fraud-api/v2' \
  -H 'X-API-KEY: secret' -H 'Content-Type: application/json' \
  -d '{"email":"eve@fraud.com","phone_number":"+14155550125","ip":"9.9.9.9","user_fullname":"Eve Test","user_dob":"1992-09-09","user_country":"US","session":"mock-session"}'
```

AML KO (sanctions):
```
curl -X POST 'http://localhost:8080/SeonRestService/aml-api/v1' \
  -H 'X-API-KEY: secret' -H 'Content-Type: application/json' \
  -d '{"user_fullname":"John Doe","user_dob":"1980-01-01","user_country":"US","custom_fields":{"scenario":"ko_compliance"}}'
```

Lists add:
```
curl -X PUT 'http://localhost:8080/SeonRestService/fraud-api/state-field/v1/' \
  -H 'X-API-KEY: secret' -H 'Content-Type: application/json' \
  -d '{"data_field":"email","value":"blocked@fraud.com","state":"blacklist","comment":"demo","expire_day":7}'
```

Labels:
```
curl -X PUT 'http://localhost:8080/SeonRestService/fraud-api/transaction-label/v2' \
  -H 'X-API-KEY: secret' -H 'Content-Type: application/json' \
  -d '[{"transaction_id":"txn_123","label":"fraud_suspected"}]'
```

Self-exclusion add:
```
curl -X PUT 'http://localhost:8080/SeonRestService/fraud-api/exclude/v1' \
  -H 'X-API-KEY: secret' -H 'Content-Type: application/json' \
  -d '{"user_ids":["u1","u2"],"emails":["x@y.com"]}'
```

Debug webhook attempts:
```
curl -X GET 'http://localhost:8080/__debug/webhook-attempts?limit=10'
```

## Error Shapes

- Success:
```
{ "success": true, "error": {}, "data": { ... } }
```

- Error:
```
{ "success": false, "error": { "code": "<CODE>", "message": "<text>" } }
```

Common codes: `AUTH_MISSING_KEY`, `AUTH_INVALID_KEY`, `VALIDATION_ERROR`, `BAD_REQUEST`, `HTTP_4xx`, `INTERNAL_ERROR`.

## Notes

- Deterministic: Same inputs (email, ip, session) produce stable IDs/scores/details.
- Webhooks: If `WEBHOOK_URL` set and request has `custom_fields.emit_webhooks=true`, service posts `transaction:status_update` with header `Digest: SHA-256=<hex(hmac)>` using `SECRET_KEY`. Inspect attempts via `/__debug/webhook-attempts`.
