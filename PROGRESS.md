# Progress - IPO Insight App

## Stage 0 - Setup
- [x] Repo structure created
- [x] Backend FastAPI initialized with CORS
- [x] Frontend React + Vite initialized with dependencies

**Status:** Completed

## Stage 1 - Historical Dataset Compilation
- [x] Compiled 32 real, verifiable historical IPOs.
- [x] Sourced specific precision-engineering peers (Gala Precision, Poojaa Precision, Omnitech Engineering).
- [x] Ensured dataset has GMP trends, issue size, ratios, subscription data, and actual listing gains.
- [x] Added `source_url` for strict auditability per AGENT_RULES.

**Status:** Completed

## Stage 2 - Allotment Calculator
- [x] Built pure, deterministic lottery math for allotment odds.
- [x] Implemented output payload to naturally support the `EXPLAIN_LAYER_COPY.md` analogy ("raffle ticket").
- [x] Created unit tests explicitly verifying Indo-MIM's 3.07x subscription.
- [x] Documented the approximation of SEBI's true algorithm limits in the explain text.

**Status:** Completed

## Stage 3 - Model Training + Validation Hardening
- [x] XGBoost Classifier + Regressor + Logistic baseline trained and saved via joblib.
- [x] Walk-forward validation: 48% overall accuracy vs ~30% naive baseline (honest, verified).
- [x] 2021 bubble fold explicitly documented (27% — feature, not bug).
- [x] Full feature leakage audit clean.

**Status:** Completed

## Stage 4 - FastAPI Endpoints
- [x] POST /api/allotment-odds, POST /api/ipo/verdict, POST /api/ipo/peers, GET /api/live-ipos
- [x] Removed duplicate CORSMiddleware registration.
- [x] ?name= query param filter verified in code.

**Status:** Completed

## Stage 5B - Scraper Extension (Rich Fields)
- [x] refresh_job.py already had all field schemas in place.
- [x] FIXED: _get_kv_from_table missing function body (silent failure on all KV lookups).
- [x] FIXED: parse_detail_page called without ipo_name → Q-Line Biotech data bled into all IPOs.
- [x] FIXED: Fallback now returns null fields + logs warning instead of wrong cross-IPO data.
- [x] FIXED: Sector extraction rebuilt with priority-ordered keyword list (no more "Research Driven").
- [x] FIXED: anchor investor rows skipped in offer_breakdown parsing (qib_pct now correct).
- [x] ADDED: scraper_errors.log handler — silent failures are now visible.
- [x] ADDED: --reparse flag for cache-only re-parse without network.
- [x] CONFIRMED: Subscription data (sub_qib/nii/retail) NOT available on ipowatch.in detail pages. Stays null for open IPOs — documented in code, handled gracefully in frontend.
- [x] 36/36 unit tests passing (scratch/test_scraper_fix.py).
- [ ] **BLOCKED: ipowatch.in unreachable from agent sandbox. User must run scraper from their machine.**

**Next action for USER:** Run `python -m backend.src.scraper.refresh_job` from your terminal.
Then check: does Fusion Klassroom show its own about text (not Q-Line Biotech)?

**Status:** Code fixed + tested. Awaiting user re-run for live verification gate.

## Stage 6 - Peer Comparison
- [x] /api/ipo/peers endpoint verified live.

**Status:** Completed

## Stage 7+ - Frontend
- [x] Next.js 16 app with landing page, IPO detail, and learn page
- [x] Search autocomplete, IPO cards, subscription dashboard, allotment calculator
- [x] Pattern match panel with peer comparison table
- [x] Fixed missing `@/lib/api`, `@/lib/helpers`, `@/lib/utils` (build blocker)
- [x] Frontend builds successfully (`npm run build`)
- [x] Deployment configs: `render.yaml`, `frontend/.env.example`, updated `DEPLOYMENT.md`

**Status:** Completed. Ready for Render/Vercel deploy.
