# NB36 Frontend

Modern React + Vite frontend for the NB36 credit card demo. It showcases a landing page, an end-to-end application flow, explainable credit policy, and static documentation pages.

- Framework: React 18 + Vite
- Styling: Tailwind (via CDN for zero-config styling)
- Animations: Framer Motion
- Icons: lucide-react
- UI patterns: Headless UI (modal, etc.)

## Contents

- index.html — Vite HTML entry; loads Tailwind CDN and mounts the React app
- src/
  - main.jsx — App bootstrap (ReactDOM.createRoot)
  - App.jsx — Renders NB36Landing
  - NB36Landing.jsx — Main landing page composed of sections and subcomponents; includes the Credit Limits accordion section (id="creditlimit")
- components/
  - apply/
    - ApplyModal.jsx — Apply flow in a modal (Headless UI)
    - ChecksList.jsx — Lists per-check results (AML, Fraud, Credit, Income)
    - TechDetails.jsx — Expandable technical JSON details
  - form/
    - ApplyPageForm.jsx — Application form (wires to backend AML-first endpoint)
    - ApplyingMinutesCard.jsx — Small UX helper
    - Layout.jsx / Section.jsx — Structure helpers
  - wizard/
    - WizardModal.jsx — Walkthrough modal using Headless UI
  - demo/
    - DemoPanel.jsx — Hidden-by-default controls for demo scenarios (e.g., force pass/review/decline)
- public/
  - credit-policy.html — Human-readable Credit Policy (two tables + narrative)
  - diagram.html — Embedded system diagram + narrative
  - images/ — Card mockups and assets
- landing.jsx — Single-file landing page variant (not used by default)
- vite.config.js — Vite config (port 5173, host enabled)
- package.json — Scripts and deps

## Quick Start

1) Install dependencies
- Requires Node 18+
- From NB36/frontend:

```
npm install
```

2) Start the dev server

```
npm run dev
```

- Opens at http://localhost:5173
- Live reload enabled

3) Build for production

```
npm run build
```

4) Preview the build

```
npm run preview
```

- Serves the dist/ bundle on port 5173 by default

## Backend Integration

The application form posts to the backend AML-first endpoint.

- Default endpoint:
  - http://localhost:9000/apply/aml-first

Where to change:
- Preferred: components/form/ApplyPageForm.jsx (form handler and API call)
- In older/single-file variant (landing.jsx): inline ApplyForm() uses fetch directly; the main modular app uses ApplyPageForm.jsx.

Tip: If deploying the backend elsewhere (e.g., Render or your own host), update the fetch URL(s).

## Sections and Navigation

- Diagram: /diagram.html (static page)
- Credit Policy: /credit-policy.html (static page with tables)
- Credit Limits accordion: On the main landing page (NB36Landing), the section id is creditlimit. The header link for “Credit Limits” points to #creditlimit.

To change the anchor:
- Header nav: NB36/frontend/src/NB36Landing.jsx, navItems entry for “Credit Limits”
- Section: NB36/frontend/src/NB36Landing.jsx, the section element id for the Credit Limits accordion

## Editing the Credit Limits Content

Location:
- NB36/frontend/src/NB36Landing.jsx
- Look for function FAQ() and the section with id="creditlimit"

Structure:
- 8 collapsible panels (details/summary) for tiers 0 → 7 (top to bottom)
- Each panel includes bullet points for AML, Fraud, Credit, and Income
- The summary line includes the limit range text (e.g., “Tier 3 — $11,200 – $14,392 limit”)

JSX Note:
- Avoid raw “<” characters in JSX text. Use words (e.g., “under”) or HTML entities (<).

## Styling

- Tailwind is loaded via CDN in index.html for rapid iteration—no Tailwind build step required.
- Existing classes in components follow a clean, modern aesthetic:
  - Rounded cards, soft borders, and subtle emerald accents
  - Framer Motion for entrance transitions
  - lucide-react for iconography

## Demo Controls and Wizard

- DemoPanel (components/demo/DemoPanel.jsx) exposes hidden controls for:
  - scenario (pass/review/decline)
  - income coverage months
- WizardModal (components/wizard/WizardModal.jsx) uses Headless UI; can be triggered via the “Launch Wizard” button.

## Static Pages

- /public/credit-policy.html — Implementation of the full credit policy narrative:
  - Tier Meaning at a Glance table
  - Tier criteria by dimension table
  - Credit Limits table
  - Clean, readable layout matching the site’s style
- /public/diagram.html — Embedded Whimsical diagram with a narrative section; anchors and copy adjusted to your preferences.

## Development Tips

- If you change anchors or ids in NB36Landing.jsx, update the header nav to match.
- Keep all large JSON-like tokens highlighted as needed by wrapping them in spans or rendering in pre blocks in static HTML pages; in JSX components, prefer text + Tailwind classes for emphasis.
- For any JSX text that needs “<”:
  - Use words (“under”) or HTML entities (<).

## Scripts

- npm run dev — Start Vite dev server
- npm run build — Build for production
- npm run preview — Preview the production build

## License

Demo code for NB36. For internal/testing/demo purposes only.
