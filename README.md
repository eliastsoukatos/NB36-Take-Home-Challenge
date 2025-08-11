# NB36 — End‑to‑End Credit Card Demo (Monorepo)

This project is a self‑contained demo of an application journey, from a public landing page and apply flow to an orchestration/policy layer with mock vendors.

It contains five independently runnable services/modules:
1) NB36 (app) — frontend (React/Vite) and backend (FastAPI)
2) SEON_API — mock SEON AML + Fraud APIs
3) Experian_API — mock Experian Credit Profile API
4) Plaid_API — mock Plaid Income APIs (payroll/bank)
5) Taktile — orchestration/policy service (AML+Fraud today), calling SEON and (optionally) other vendors

Each module can be started on its own and tested via curl/UI, or you can run them together and see the full flow.

- Frontend: React 18 + Vite + Tailwind (CDN), Framer Motion, lucide-react
- Backend/Services: FastAPI (Python 3.10/3.11+)

## Repository Layout

- NB36/
  - frontend/ — React website and apply flow (Vite dev server: 5173)
  - backend/ — Minimal API that delegates orchestration to Taktile (port: 9000)
- SEON_API/ — Mock SEON AML and Fraud (default port: 8081 used in examples)
- Experian_API/ — Mock Experian Credit Profile v2 (port: 8000)
- Plaid_API/ — Mock Plaid Income (port: 8200)
- Taktile/ — Orchestrator/policy (port: 9100)

Static docs:
- NB36/frontend/public/diagram.html — System diagram and narrative
- NB36/frontend/public/credit-policy.html — Human‑readable credit policy

## Ports & URLs (defaults)

- Frontend (Vite): http://localhost:5173
- NB36 Backend: http://localhost:9000
- Taktile: http://localhost:9100
- SEON_API: http://localhost:8081 (we run it on 8081 to match Taktile defaults)
- Experian_API: http://localhost:8000
- Plaid_API: http://localhost:8200

If you change any of these, be sure to update the corresponding BASE_URLs and client endpoints listed below.

## Requirements

- Node.js 18+ (Vite 5 requires Node 18+)
- Python 3.11 recommended (some modules accept 3.10+, but 3.11 works everywhere)
- pip (or a virtualenv/conda environment)

## Quickstart — Run Everything

Open four terminals (or use a process manager). From the repo root:

1) SEON mock (port 8081)
```
pip install -r SEON_API/requirements.txt
python -m uvicorn SEON_API.app.main:app --reload --port 8081
```
Config of interest (env vars):
- API_KEY=secret (default)
- SECRET_KEY=devsecret (webhook signing)
- WEBHOOK_URL (optional)

2) Taktile orchestrator (port 9100)
```
pip install -r Taktile/requirements.txt
python -m uvicorn Taktile.service.main:app --reload --port 9100
```
Config (env or Taktile/service/config.py):
- SEON_BASE_URL=http://localhost:8081
- API_KEY_SEON=secret
- (If you wire more vendors later, set EXPERIAN_BASE_URL, PLAID_BASE_URL, etc.)

3) NB36 backend (port 9000)
```
pip install -r NB36/backend/requirements.txt
python -m uvicorn NB36.backend.app.main:app --reload --port 9000
```
Config (env or NB36/backend/app/config.py):
- TAKTILE_BASE_URL=http://localhost:9100

4) NB36 frontend (Vite dev server: 5173)
```
cd NB36/frontend
npm install
npm run dev
```
- The apply form posts to http://localhost:9000/apply/aml-first by default (update if backend is elsewhere)
- Open http://localhost:5173

Optional (other vendors):
- Experian_API (8000)
  ```
  pip install -r Experian_API/requirements.txt
  python -m uvicorn Experian_API.app.main:app --reload --port 8000
  ```
  Taktile config knobs (if you extend): EXPERIAN_BASE_URL, EXPERIAN_TOKEN, EXPERIAN_CLIENT_REF
- Plaid_API (8200)
  ```
  pip install -r Plaid_API/requirements.txt
  python -m uvicorn Plaid_API.main:app --reload --port 8200
  ```
  Auth defaults: see Plaid_API/README.md (client_id/secret headers/envs); all responses 200 with error envelope except PDF

## Running Modules Independently

You can start any single service on its own.

- NB36/frontend alone
  - `npm run dev` and browse the site. The apply form will fail if backend isn’t running; you can still review UI and static pages (diagram, policy).
- NB36/backend alone
  - Start the backend and send POST /apply/aml-first with an intake payload. You’ll need Taktile up (or change backend config to a mock).
- Taktile alone
  - Start Taktile and call `POST /workflows/kyc/aml-first` with `{ case_id, intake }`. You’ll need SEON mock reachable at SEON_BASE_URL. See Taktile/runner scripts.
- SEON_API alone
  - Start SEON and hit its AML or Fraud endpoints with curl; supports scenarios (pass/review/ko_*).
- Experian_API alone
  - Start Experian mock and hit `POST /v2/credit-report`; supports scenarios and vendor error simulation.
- Plaid_API alone
  - Start Plaid mock and call payroll/bank endpoints; supports force_mode, coverage_months, risk, and PDF.

## Configuration Matrix

SEON_API
- PORT (default 8081 in examples)
- API_KEY=secret (header: X-API-KEY)
- SECRET_KEY=devsecret (for webhook HMAC)
- WEBHOOK_URL (optional; posts if `custom_fields.emit_webhooks=true`)

Taktile
- SEON_BASE_URL=http://localhost:8081
- API_KEY_SEON=secret
- Optional if extending: EXPERIAN_BASE_URL=http://localhost:8000, EXPERIAN_TOKEN=sandbox-token, EXPERIAN_CLIENT_REF=SBMYSQL, PLAID_BASE_URL=http://localhost:8200, etc.

NB36 Backend
- TAKTILE_BASE_URL=http://localhost:9100

Experian_API
- No env required; headers drive auth; see README for `Authorization: Bearer sandbox-token`, `clientReferenceId: SBMYSQL`, etc.

Plaid_API
- PLAID_CLIENT_ID / PLAID_SECRET (optional). If set, credentials must match; otherwise any non‑empty strings are accepted.

NB36 Frontend
- Apply form targets http://localhost:9000/apply/aml-first (edit in components/form/ApplyPageForm.jsx if needed)
- Static docs:
  - /credit-policy.html — longform policy (with two tables)
  - /diagram.html — embedded Whimsical system diagram and narrative
- Anchors:
  - Credit Limits accordion section id is `creditlimit`
  - Header link points to `#creditlimit`

## Verifying End‑to‑End

1) Start SEON → Taktile → NB36 Backend → NB36 Frontend (in that order).
2) Open http://localhost:5173 and complete the form.
3) Use the demo panel (hidden in UI by design) or craft inputs to influence `custom_fields.scenario`:
   - pass → AML PROCEED + Fraud PASS (provisional tier)
   - review → Fraud REVIEW
   - ko_compliance → AML DECLINE

You should see a decision payload reflected in the UI with case_id and details.

## Editing URLs Safely

- If you move any service to a new host/port:
  - Update backend’s TAKTILE_BASE_URL
  - Update Taktile’s SEON_BASE_URL (and any other vendor BASE_URLs you wire in)
  - Update the frontend apply URL in NB36/frontend/components/form/ApplyPageForm.jsx
- Keep ports unique and accessible from localhost; consider CORS if crossing origins in production.

## Common Issues

- Raw “<” in JSX:
  - JSX treats `<` as an HTML tag start. Use words (“under”) or HTML entities (`<`) in text.
- 401/403 from SEON mock:
  - Ensure `X-API-KEY: secret` and API_KEY env set to the same value.
- 5xx/Timeouts from Experian/Plaid mocks:
  - These can be intentionally forced using the mock’s scenario toggles; check their READMEs.
- Cross‑service mismatch:
  - If Taktile can’t reach SEON, verify SEON_BASE_URL and port.

## Scripts Reference

NB36/frontend
- `npm run dev` — Vite dev server
- `npm run build` — Build to dist/
- `npm run preview` — Preview dist/ on 5173

Taktile
- `python -m uvicorn Taktile.service.main:app --reload --port 9100`
- Runners:
  - `python Taktile/runner/orchestrate_full_kyc.py [scenario]`
  - `python Taktile/runner/orchestrate_aml.py [ko_compliance]`

NB36/backend
- `python -m uvicorn NB36.backend.app.main:app --reload --port 9000`

SEON_API
- `python -m uvicorn SEON_API.app.main:app --reload --port 8081`

Experian_API
- `python -m uvicorn Experian_API.app.main:app --reload --port 8000`

Plaid_API
- `python -m uvicorn Plaid_API.main:app --reload --port 8200`

## Licenses & Intended Use

This is a demonstration project. The mock services emulate vendor responses for product/design/engineering exploration and are not suitable for production.
