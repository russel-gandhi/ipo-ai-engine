# Build Stages — IPO Insight App

Work through in order. Don't skip ahead to frontend/animation work before the
backend is verified with real data — see AGENT_RULES.md §2-3.

---

## Stage 0 — Setup
- Repo structure per PROJECT_ARCHITECTURE.md §4
- `backend/requirements.txt`: fastapi, uvicorn, scikit-learn, pandas,
  requests, beautifulsoup4 (or whatever the scraper needs), pytest
- `frontend`: `npm create vite@latest` with React + TypeScript template,
  install tailwindcss, framer-motion, recharts (or visx), axios/fetch wrapper

**Done when:** backend runs a hello-world FastAPI endpoint, frontend runs a
blank Vite dev server, both confirmed working locally.

---

## Stage 1 — Historical Dataset Compilation
**This is the most important and most tedious stage — don't rush it.**

- Compile 30-80 historical IPOs into `historical_ipos.csv`: company, sector,
  issue_size, fresh_vs_ofs_ratio, price_band, subscription figures (retail/
  NII/QIB/overall), GMP trend data, actual listing_gain_pct
- Source from Chittorgarh's historical archive and similar public sources —
  keep a `source_url` column per row for auditability (AGENT_RULES.md §4)
- Include the precision-engineering/auto-ancillary peer companies already
  identified (Gala Precision, Poojaa Precision, Omnitech Engineering, etc.)
  so the peer-comparison feature (Stage 6) has real data to draw from

**Done when:** a CSV with real, sourced rows exists, spot-checked by hand for
at least 5 entries against the original source to confirm accuracy.

---

## Stage 2 — Allotment Calculator (build this early, it's your safety net)
**Build:** `backend/src/allotment/calculator.py`

- Implement the proportionate lottery probability math per
  PROJECT_ARCHITECTURE.md §6
- Unit tests with known real subscription multiples, sanity-checked by hand

**Done when:** tested against at least one real IPO's actual subscription
data (e.g. Indo-MIM's ~3.07x) and the output probability is a sane, explain
-able number you'd trust to show your dad.

---

## Stage 3 — Model Training
**Build:** `backend/src/model/train.py`, `features.py`

- Feature engineering per PROJECT_ARCHITECTURE.md §5
- Train a Random Forest or Gradient Boosted Trees classifier on bucketed
  listing-gain outcomes
- Run k-fold or leave-one-out cross-validation given the small dataset —
  print and record the REAL cross-validated accuracy, not training accuracy

**Done when:** you have a saved trained model, an honestly-reported
cross-validation score, and can show real feature importances that make
intuitive sense (e.g. GMP trend and subscription level should rank high).

---

## Stage 4 — Prediction API
**Build:** `backend/src/model/predict.py`, `main.py` routes

- `/api/ipo/{id}/verdict` and `/api/ipo/{id}/prediction-factors` endpoints
- `/api/allotment-odds` endpoint wrapping Stage 2's calculator
- Confidence/sample-size shown alongside every prediction, per
  AGENT_RULES.md §1

**Done when:** hitting these endpoints with real IPO data (including
Indo-MIM's current numbers) returns real, sane, non-fabricated JSON —
verified by printing/inspecting actual responses, not just checking for a
200 status code.

---

## Stage 5 — Live Data Scraper
**Build:** `backend/src/scraper/refresh_job.py`

- Pulls current GMP/subscription for tracked live IPOs (starting with
  Indo-MIM) from public sources on a schedule (~every 15 min)
- Defensive error handling: retries, fallback to last-known-good data,
  never crashes the API (AGENT_RULES.md §4)
- Writes to `live_ipos.json` with a `last_updated` timestamp

**Done when:** confirmed working against the real live Indo-MIM data, AND
confirmed to fail gracefully when you deliberately break it (e.g. point it
at a bad URL temporarily) — per AGENT_RULES.md §7 testing checklist.

---

## Stage 6 — Peer Comparison Endpoint
**Build:** `/api/ipo/{id}/peers` route

- Returns peer IPOs (from Stage 1's dataset) with the model's retroactive
  prediction vs. their actual real outcome
- This is your credibility-proof feature — make sure the peer list actually
  includes companies genuinely comparable to whatever IPO is selected, not
  just arbitrary rows

**Done when:** querying for an IPO like Indo-MIM returns a real peer list
(Gala Precision, Poojaa Precision, etc.) with real actual-outcome data.

---

## Stage 7 — Frontend: Core Screens (minimal styling first)
**Build:** React components per PROJECT_ARCHITECTURE.md §4 repo structure

- Verdict card, allotment calculator form, GMP trend chart, peer comparison
  table — wired to the real backend API, NOT mock data
- Get this working with default/minimal styling BEFORE moving to Stage 8 —
  confirm real data flows end-to-end through the UI first

**Done when:** a user can open the app, see Indo-MIM's real current data,
enter their own application details into the allotment calculator, and get
a real computed probability back — all through the UI, no manual API calls
needed.

---

## Stage 8 — Design System Implementation
**Build:** apply DESIGN_BRIEF.md tokens — colors, Fraunces/Space Grotesk/IBM
Plex Mono typography, button states, layout per the ASCII wireframe

- Build the CertaintySpectrum component ONCE, reuse everywhere a
  probability/confidence appears
- Build the ExplainLayer accordion ONCE, reuse for every metric's ⓘ

**Done when:** the app visually matches the design brief's intent — run the
self-critique checklist at the end of DESIGN_BRIEF.md before moving on.

---

## Stage 9 — Motion & Animation Polish
**Build:** Framer Motion transitions, chart animation tuning per
DESIGN_BRIEF.md "Motion principles"

- Staggered verdict card reveal, accordion layout animation, certainty
  spectrum spring animation, chart data-update transitions
- This is the LAST thing polished, and the safest thing to keep iterating
  on right up to the deadline (AGENT_RULES.md §5)

**Done when:** the app feels fluid and intentional, not because of one
flashy effect but because of consistent, restrained motion throughout.

---

## Stage 10 — Deployment (Render)
See DEPLOYMENT.md for full details.

**Done when:** the app is live at a public Render URL, backend and frontend
both actually serving real data end-to-end (not just working on localhost) —
verified per AGENT_RULES.md §6.

---

## Stage 11 — README & Polish
- Explain the allotment math, the model's real cross-validated accuracy, the
  dataset size and sourcing honestly, the design concept (certainty
  spectrum), and clear "Known Limitations" / "Not Financial Advice" sections
- Record a short demo clip/GIF
- Link the live Render deployment prominently

---

## Minimum Viable Submission (if time runs out)
In order of preference:
1. Stages 0-2 + 7 (allotment calculator, fully working, in a clean but
   simply-styled UI) + Stage 10 (deployed) + Stage 11 (honest README) — a
   smaller, completely honest, fully working tool beats a bigger broken one.
2. Add Stages 3-6 (model + peers) if time allows, styling per Stage 8-9 last.

Never skip Stage 1's real data sourcing to save time by fabricating rows —
per AGENT_RULES.md Rule 0, this is the one shortcut that's off the table
entirely, no matter how tight the clock gets.
