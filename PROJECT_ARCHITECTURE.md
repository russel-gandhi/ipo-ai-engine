# Project Architecture — IPO Insight App

## 1. What this app does
Helps a retail investor understand an IPO before committing money, via two
genuinely solid, honest components:
1. **Allotment odds calculator** — deterministic math, tells you the
   probability your application actually gets shares given the subscription
   level in your category. No ML needed, no ambiguity, always correct.
2. **Historical pattern analysis** — shows how IPOs with similar
   characteristics (GMP trend, subscription level, sector, OFS ratio)
   historically performed on listing day, framed as pattern-matching, NOT as
   a guaranteed prediction.

Both are surfaced through an explainable, dual-audience UI (see
UI_UX_SPEC.md) with a distinctive, non-templated design (see DESIGN_BRIEF.md).

## 2. Explicit non-goals (say this in the README too)
- This is NOT a financial advisory tool and does not claim regulatory
  compliance as one (SEBI-registered advisors exist for a reason)
- This does NOT guarantee any listing outcome
- This does NOT execute trades or connect to any brokerage/banking account
- Small training dataset (dozens of IPOs, not thousands) — treat all
  predictions as directional pattern signals, not precise forecasts, and say
  so in the UI itself (see verdict card copy in UI_UX_SPEC.md §4)

## 3. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│                                                                    │
│  historical_ipos.csv  — compiled dataset of past IPOs:            │
│    company, sector, issue_size, fresh_vs_ofs_ratio, price_band,   │
│    lot_size, subscription_retail/nii/qib/overall, gmp_day1,       │
│    gmp_final, gmp_trend (rising/falling/flat), listing_gain_pct,  │
│    listing_gain_bucket (loss/flat/moderate/high)                  │
│                                                                    │
│  refresh_job.py — scheduled scraper (every ~15 min while an       │
│    IPO is open) pulling current GMP + subscription for TRACKED    │
│    live IPOs from public sources, writes to live_ipos.json         │
│    with a last_updated timestamp                                  │
└─────────────────────────────┬──────────────────────────────────┘
                               │
┌─────────────────────────────▼──────────────────────────────────┐
│                    BACKEND (FastAPI)                              │
│                                                                    │
│  /api/ipo/{id}/verdict          → verdict category + headline     │
│                                    metrics + disclaimer text        │
│  /api/ipo/{id}/prediction-factors → feature importance breakdown  │
│  /api/ipo/{id}/peers            → peer comparison list w/ actual  │
│                                    outcomes                          │
│  /api/allotment-odds             → POST: category, lots, sub.      │
│                                    multiple → probability            │
│  /api/ipo/{id}/gmp-history       → time series for the chart       │
│  /api/ipos                       → list of tracked IPOs (live +    │
│                                    historical)                       │
│                                                                    │
│  src/model/                                                        │
│    train.py        — trains classifier on historical_ipos.csv      │
│    predict.py       — loads trained model, returns bucket +         │
│                        confidence + factor breakdown (feature        │
│                        importances, e.g. via a simple tree model     │
│                        so importances are directly interpretable,    │
│                        not needing a separate SHAP step unless        │
│                        time allows)                                  │
│  src/allotment/                                                     │
│    calculator.py    — pure math, lottery/proportionate allotment     │
│                        probability given subscription multiple        │
│  src/scraper/                                                       │
│    refresh_job.py   — pulls current GMP/subscription for tracked     │
│                        live IPOs                                     │
└─────────────────────────────┬──────────────────────────────────┘
                               │ JSON only
┌─────────────────────────────▼──────────────────────────────────┐
│                 FRONTEND (React + Vite)                            │
│  Verdict card · GMP trend chart · Allotment calculator ·           │
│  Peer comparison · Explain-layer accordions · Certainty spectrum   │
│  component (see DESIGN_BRIEF.md)                                  │
│  Fetches from FastAPI backend, renders only — no business logic    │
│  duplicated in the frontend                                         │
└──────────────────────────────────────────────────────────────────┘
```

## 4. Repo Structure

```
ipo-insight-app/
├── README.md
├── PROJECT_ARCHITECTURE.md      (this file)
├── AGENT_RULES.md
├── STAGES.md
├── DESIGN_BRIEF.md
├── UI_UX_SPEC.md
├── DEPLOYMENT.md
├── backend/
│   ├── requirements.txt
│   ├── main.py                   # FastAPI app + routes
│   ├── src/
│   │   ├── model/
│   │   │   ├── train.py
│   │   │   ├── predict.py
│   │   │   └── features.py       # feature engineering, shared by train+predict
│   │   ├── allotment/
│   │   │   └── calculator.py
│   │   ├── scraper/
│   │   │   └── refresh_job.py
│   │   └── data/
│   │       ├── historical_ipos.csv
│   │       └── live_ipos.json
│   └── tests/
│       ├── test_allotment.py
│       ├── test_model.py
│       └── test_api.py
└── frontend/
    ├── package.json
    ├── src/
    │   ├── components/
    │   │   ├── VerdictCard.tsx
    │   │   ├── CertaintySpectrum.tsx   # the signature component, built once, reused everywhere
    │   │   ├── GmpTrendChart.tsx
    │   │   ├── AllotmentCalculator.tsx
    │   │   ├── PeerComparison.tsx
    │   │   ├── ExplainLayer.tsx        # the accordion ⓘ pattern, reused everywhere
    │   │   └── PredictionFactors.tsx
    │   ├── api/
    │   │   └── client.ts               # typed fetch wrapper for backend endpoints
    │   └── App.tsx
    └── index.html
```

## 5. The Model (keep this honest and simple)
- **Algorithm:** a simple, interpretable model — Random Forest or Gradient
  Boosted Trees (via scikit-learn) classifying into gain buckets (loss / flat
  / moderate 0-25% / high 25%+), NOT a raw regression predicting an exact
  percentage. A bucket with a confidence score is honest about precision
  limits; a single "+33.7% predicted" number is not, given the dataset size.
- **Features:** subscription multiple (overall + by category), GMP % at
  various points before close, GMP trend direction, fresh-issue-vs-OFS
  ratio, issue size, sector (categorical), price-band width
- **Feature importance:** use the model's native feature_importances_ (tree
  models give this for free) to power the "what influenced this prediction"
  bar list in the UI — no need for a separate explainability library unless
  time allows
- **Validation:** leave-one-out or k-fold cross-validation given the small
  dataset size — report and DISPLAY the cross-validated accuracy honestly in
  the README, do not cherry-pick a good train-set fit and present it as
  real-world accuracy

## 6. The Allotment Calculator (build this first, it's your safety net)
Pure probability math, no ML:
- Input: category (Retail/sNII/bNII/QIB — each has different allotment
  rules), number of lots applied, subscription multiple for that category
- Retail category in India uses proportionate lottery allotment when
  oversubscribed: if subscription multiple is S, roughly `1/S` chance per
  lot-application of being selected in the lottery draw for at least one lot
  (simplify to this model, note in the explain-layer that the exact SEBI
  lottery algorithm has additional nuances that this approximates)
- This calculator has ZERO dependency on the ML model or live data — it
  should work standalone, instantly, and be bulletproof. Treat it as the
  part of the app that must never break.

## 7. Known Risks (flag early)
- **Historical dataset size** — realistically 30-80 rows compiled manually
  or scraped from Chittorgarh/similar sources. This is small for ML. Be
  upfront about it everywhere it matters (README, UI disclaimer, verdict
  card copy).
- **Scraper fragility** — public IPO data sites change their HTML/structure
  without notice. Build the scraper defensively (explicit error handling,
  fallback to last-known-good data with a visible staleness indicator) per
  UI_UX_SPEC.md §7 — never let a scraper failure crash the app or silently
  show blank data.
- **Render free-tier cold starts** — if deploying the backend on Render's
  free tier, the API may sleep after inactivity and take 30-60s to wake on
  first request. Handle this gracefully in the frontend (loading state, not
  a broken blank screen) — see DEPLOYMENT.md.
