# IPO-AI Engine 🚀

A state-of-the-art, SEBI-compliant financial technology platform designed to help retail and institutional investors make data-driven decisions on Initial Public Offerings (IPOs) in the Indian Stock Market.

## Core Pillars
1. **Strict SEBI Compliance:** The allotment calculator strictly follows SEBI's proportionate lottery guidelines, accurately limiting retail quotas and mapping PAN applications without false probability inflation.
2. **Anti-Overfitting AI:** Our ML Pipeline utilizes an honest Walk-Forward Validation architecture (time-series based). Models are exclusively tested on data they could not have seen beforehand.
3. **Credibility through Proof-of-Work:** Rather than acting as a black-box, the engine retrieves the closest historical peers by sector and issue size to validate its confidence scores.
4. **Resilient Data Scraping:** Live data is fetched through isolated background asyncio threads that aggressively cache data, ensuring the API is never blocked during an active scraping session.

## Current State (Phase 1 Complete)
The powerful backend "Brain" is fully operational, built in **Python (FastAPI)** and featuring:
- An **XGBoost Classifier & Regressor** pipeline that produces confidence-bounded Historical Gain Ranges rather than falsely precise point estimates.
- A **Logistic Regression Baseline** to penalize low-confidence predictions.
- **211 Curated Historical IPOs** tagged strictly for out-of-sample validation.
- Live background scraping syncing current Grey Market Premium (GMP) data.

## API Architecture
The following endpoints are active via the FastAPI instance:
- `POST /api/allotment-odds` - Computes precise, PAN-masked lottery probabilities.
- `POST /api/ipo/verdict` - Evaluates current metrics to output a predicted listing bucket, a historical gain range, and a dynamic confidence score based on baseline-agreement and real peer density.
- `POST /api/ipo/peers` - Fetches historical peers for credibility validation.
- `GET /api/live-ipos` - Yields the live background-cached scraping data.

## Getting Started

### Backend
```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.src.main:app --port 8000
```
This automatically launches background scrapers and serves ML inferences.

### Frontend
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```
Open http://localhost:3000 — the dashboard connects to the API at http://localhost:8000.

## Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for Render/Vercel setup. A `render.yaml` blueprint is included at the repo root.

---
*Phase 2 (Next.js Frontend Dashboard) is complete. Deploy via Render Blueprint or Vercel.*
