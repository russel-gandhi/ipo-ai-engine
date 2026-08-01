# IPO-AI Engine

> "India's first IPO analysis platform that publishes its own miss rate."

`120 verified historical IPOs` | `48% walk-forward accuracy (vs 25% random baseline)` | `0 hardcoded predictions`

![Analysis Dashboard](docs/screenshots/dashboard.png)

---

## The Honest Summary

IPO-AI Engine is a dual-mode web platform designed to give Indian retail investors transparent, explainer-first analysis for Initial Public Offerings. Unlike conventional platforms that conceal prediction failures behind proprietary black-box ratings, IPO-AI Engine surfaces its retroactive accuracy, backtesting peer deltas, and model confidence scores alongside every data point. The platform combines real-time scraped market metrics, SEBI-compliant allotment math, and a walk-forward-validated machine learning engine to evaluate issues without hype. It is not a prediction or recommendation tool — it is a transparency dashboard that puts historical pattern matching and educational context ahead of speculation.

---

## What Makes This Different

1. **Proof of Work table** — Displays every historical peer comparison including prediction misses alongside a published hit rate. Unlike commercial portals that hide past errors, every evaluation is paired with verifiable backtesting deltas.
2. **Walk-forward validated, not backtested** — Built on strict chronological walk-forward validation after detecting and fixing a target leakage bug in GMP features that produced fraudulent 100% accuracy. The true, audited out-of-sample accuracy is 48%.
3. **Confidence scores from real factors** — Evaluates confidence dynamically using real peer density, per-bucket historical walk-forward accuracy, model agreement between XGBoost and Logistic baselines, and source conflict flags rather than arbitrary percentages.
4. **2021 regime warning** — Explicitly flags matches against the 2021 bull-market window where model accuracy dropped to 27%. Surfaces market-regime underperformance rather than smoothing over volatile historical anomalies.
5. **Education at every data point** — Every metric includes CSS-only context tooltips, while the allotment calculator details exact mathematical steps. Built to inform first-time retail applicants and experienced investors alike.
6. **SEBI allotment math engine** — Corrects the widespread retail misconception that submitting multiple lots on a single PAN increases allotment probability by enforcing SEBI's deterministic 1-lot-per-PAN lottery formula.

---

## Architecture

### System Architecture Diagram

```
[ipowatch.in / chittorgarh.com]
         |
         | (Playwright + BeautifulSoup, every 15 min)
         v
[refresh_job.py — Background Scraper]
         |
         | (writes to)
         v
[live_ipos.json — Local Cache]
         |
[historical_ipos.csv — 120 real_scraped rows]
         |
         | (train.py — walk-forward validated)
         v
[XGBoost Classifier] + [XGBoost Regressor] + [Logistic Baseline]
         |
         v
[FastAPI — main.py — Port 8000]
    |         |          |
    |         |          |
/allotment  /verdict   /peers
  -odds               
    |         |          |
    v         v          v
[Next.js App Router — Port 3000]
    |
    |--- / (Landing + Search)
    |--- /analyse/[slug] (7-section dashboard)
    |--- /learn (5-section education hub)
```

### Backend Components

| File | Purpose | Key Detail |
|---|---|---|
| `calculator.py` | SEBI allotment math engine | Deterministic proportionate lottery calculation, 1-lot-per-PAN cap enforced |
| `refresh_job.py` | Background scraper | Playwright + BeautifulSoup, 15-min refresh cycle, null-not-wrong fallback, `scraper_errors.log` |
| `train.py` | Model training + walk-forward validation | Dynamic folds ($N \ge 15$), `DummyClassifier` baseline, confusion matrix per fold |
| `features.py` | Feature engineering pipeline | `RelativeIssueSizeTransformer` fits on train fold only — no test-set leakage |
| `main.py` | FastAPI server | 4 active endpoints, async background scraper, CORS configured for frontend |
| `peers.py` | Proof of Work engine | Fold-specific retroactive retraining per peer — no future-data leakage in historical predictions |
| `historical_ipos.csv` | Training dataset | 120 `real_scraped` + 91 `synthetic_interpolated` (tagged, excluded from validation) |

### Frontend Components

| File | Purpose | Key Detail |
|---|---|---|
| `SearchBar.tsx` | Live IPO search | 200ms debounce, server-side `?name=` filter query |
| `Tooltip.tsx` | Inline explainers | CSS-only popover, no library dependencies, present on every data metric |
| `AllotmentCalculator.tsx` | SEBI math UI | Renders step-by-step math, corrects multi-lot PAN misconceptions |
| `PeerTable.tsx` | Proof of Work UI | Renders all historical peers including misses with 2021 regime warning flags |
| `helpers.ts` | Slug & display utils | `toSlug`, `fromSlug`, `getSectorBadge`, `getStatusBadge`, `formatRupee` |
| `/analyse/[slug]/page.tsx` | Dynamic analysis page | 7 interactive sections, all data loaded dynamically from API, zero hardcoded IPO data |

---

### ML Pipeline

1. **Data sourcing** — 120 verified, scraped historical Indian IPOs (mainboard and SME segments) tagged by data origin. 91 synthetic interpolated rows are explicitly tagged and excluded from model training and out-of-sample validation.
2. **Feature engineering** — 14 structured features including GMP trajectory slope, per-category subscription multiples (QIB, NII, Retail), anchor allocation percentage, trailing 30-day Nifty market regime index, and sector-relative issue size (transformed via custom `scikit-learn` Transformer fitted exclusively on training folds).
3. **Leakage audit** — Every feature underwent a strict data leakage audit. An initial inspection revealed that GMP trend features were accidentally derived using post-listing actual performance, producing fraudulent 100% test accuracy. The pipeline was restructured to enforce complete temporal isolation, reducing accuracy to an honest 48%.
4. **Walk-forward validation** — Evaluated using rolling chronological windows ($N \ge 15$ test samples per fold) without fold overlap, ensuring the model trains exclusively on historical data prior to each test window. Every fold is benchmarked against `DummyClassifier` and `DummyRegressor` baselines.
5. **Ensemble Architecture** — Primary XGBoost Classifier for bucket estimation (`loss`, `flat`, `moderate`, `high`), secondary XGBoost Regressor for listing gain percentage ranges, and a Logistic Regression baseline. Model agreement is tracked and exposed in the API payload.
6. **Honest Results Matrix:**

| Test Window | Train N | Test N | Classifier Acc | Naive Acc | Regressor MAE | Naive MAE |
|---|---|---|---|---|---|---|
| 2019-12 to 2020-08 | 36 | 15 | 67% | 47% | 11.22% | 21.25% |
| 2020-09 to 2021-02 | 51 | 15 | 53% | 33% | 13.19% | 19.46% |
| 2021-03 to 2021-09 | 66 | 15 | 27% | 7% | 17.18% | 11.21% |
| 2021-10 to 2022-04 | 81 | 15 | 60% | 40% | 12.20% | 14.88% |
| 2022-04 to 2023-02 | 96 | 24 | 38% | 25% | 11.59% | 12.74% |
| **Overall** | — | — | **48%** | **~30%** | — | — |

*Note on 2021-03 to 2021-09 fold:* During the peak 2021 tech IPO bull market (Zomato, Nykaa, Paytm), market valuation multiples detached from historical baselines, causing model accuracy to drop to 27%. Rather than discarding this fold, the platform explicitly surfaces 2021 matches with a prominent regime warning badge.

---

## API Reference

### 1. `POST /api/allotment-odds`
Computes SEBI-compliant proportionate allotment odds across single or multi-PAN family applications.

**Request:**
```json
{
  "sub_retail": 3.07,
  "num_pans": 2,
  "category": "Retail"
}
```

**Response:**
```json
{
  "category": "Retail",
  "masked_pan": "⁕⁕⁕⁕⁕⁕1234F",
  "probability_pct": 32.57,
  "probability_at_least_one_lot": 0.5454,
  "odds_per_pan": 0.3257,
  "expected_lots": 0.65,
  "allotment_regime": "Proportionate Lottery",
  "explain_text": "With Retail category subscribed 3.07x, each PAN has a 32.6% chance of allotment.",
  "guardrail": "Applying for multiple lots on the same PAN does NOT increase your allotment probability.",
  "privacy_note": "PAN data lives strictly in volatile memory and is never written to persistent storage."
}
```

### 2. `POST /api/ipo/verdict`
Evaluates IPO metrics using XGBoost and Logistic Regression to generate a historical pattern match.

**Request:**
```json
{
  "issue_size": 1800.0,
  "fresh_vs_ofs_ratio": 0.5,
  "sub_retail": 3.07,
  "sub_nii": 8.4,
  "sub_qib": 18.2,
  "sub_overall": 9.9,
  "price_band": 225.0,
  "sector": "Energy",
  "gmp_trend": "rising",
  "is_sme": false
}
```

**Response:**
```json
{
  "bucket_estimate": "moderate",
  "historical_gain_range": "15-35%",
  "confidence_score": "Moderate (5 peers, 48% walk-forward acc)",
  "real_peer_count": 5,
  "walk_forward_accuracy_for_bucket": 0.48,
  "model_agreement": true,
  "disclaimer": "All outputs are generated via historical pattern matching against past Indian IPO listings. Never interpret predictions as buy/sell recommendations."
}
```

### 3. `POST /api/ipo/peers`
Retrieves retroactively evaluated historical peers for proof-of-work validation.

**Request:**
```json
{
  "issue_size": 1800.0,
  "sector": "Energy"
}
```

**Response:**
```json
{
  "target_sector": "Energy",
  "target_issue_size": 1800.0,
  "peer_hit_rate": "Model was within ±15% of actual listing gain in 4 out of 5 similar past IPOs.",
  "peers": [
    {
      "company_name": "ACME Solar Holdings",
      "sector": "Energy",
      "issue_size": 2900.0,
      "actual_listing_gain_pct": 12.5,
      "retroactive_bucket_estimate": "moderate",
      "retroactive_gain_range": "15-35%",
      "delta": -2.5,
      "regime_warning": false,
      "similarity_score": "Same Sector"
    }
  ]
}
```

### 4. `GET /api/live-ipos`
Returns cached live IPO data scraped from primary market portals with optional name filtering.

**Request:**
```http
GET /api/live-ipos?name=juniper HTTP/1.1
```

**Response:**
```json
{
  "last_updated": "2026-08-01T12:00:00Z",
  "ipos": [
    {
      "name": "Juniper Green Energy",
      "gmp": 10.0,
      "price_band": 225.0,
      "status": "open",
      "sector": "Energy",
      "issue_size": 1800.0
    }
  ]
}
```

---

## Setup & Running Locally

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Install Playwright browser dependencies for background scraper
playwright install chromium

# Launch FastAPI server on port 8000
python -m uvicorn backend.src.main:app --reload --port 8000
```

*Note on scraping:* The background scraper fetches live metrics from primary market sources. When executing inside restricted cloud sandboxes or datacenters, Cloudflare protection may cause connection timeouts. Run on a residential IP network for active scraping.

### Frontend Setup

```bash
cd frontend
npm install

# Launch Next.js dev server on port 3000
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Data & Model Notes

The underlying dataset contains 120 verified historical Indian IPO listings. While 120 rows provide sufficient sample density for a 4-bucket classification model, regression point estimates remain constrained by sample variance across rare sectors. This is why listing gains are presented strictly as bounded ranges (`15-35%`) rather than exact decimal predictions.

Leave-One-Out Cross-Validation (LOOCV) was deliberately avoided. In financial time-series data, LOOCV introduces temporal leakage by training on future market regimes to predict past listings. Chronological walk-forward validation is harder and yields lower baseline accuracy (48% vs >70% LOOCV), but reflects true out-of-sample performance.

Synthetic data policy: 91 synthetic interpolated rows were generated during exploratory testing. These rows are tagged and strictly excluded from model training, feature fitting, and validation matrices. Expanding the core dataset to 500+ verified historical listings would allow smaller chronological fold windows, tighter regressor range bounds, and higher per-sector peer density.

---

## What This Is Not

- **Not a SEBI-registered Investment Adviser or Research Analyst.**
- **Not a prediction engine** — all outputs represent historical pattern matching against past market data.
- **Not a trading signal** — the platform deliberately omits terms like "buy", "sell", "target price", or "verdict" across all interfaces.
- **Not production-ready for real capital allocation decisions** without formal financial audit and compliance review.

---

## Project Structure

```
ipo-ai-engine/
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── calculator.py
│   │   ├── scraper/
│   │   │   └── refresh_job.py
│   │   ├── model/
│   │   │   ├── train.py
│   │   │   ├── features.py
│   │   │   └── peers.py
│   │   ├── api/
│   │   │   └── schemas.py
│   │   └── data/
│   │       ├── historical_ipos.csv
│   │       ├── live_ipos.json
│   │       └── scraper_errors.log
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── analyse/[slug]/page.tsx
│   │   │   └── learn/page.tsx
│   │   ├── components/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── IpoCard.tsx
│   │   │   ├── Tooltip.tsx
│   │   │   ├── AllotmentCalculator.tsx
│   │   │   └── PeerTable.tsx
│   │   └── lib/
│   │       ├── api.ts
│   │       └── helpers.ts
│   └── package.json
└── README.md
```
