# IPO-AI Engine: Project Overview & Master Plan

## 1. Project Vision
The **IPO-AI Engine** is a state-of-the-art, SEBI-compliant financial technology platform designed to help retail and institutional investors make data-driven decisions on Initial Public Offerings (IPOs) in the Indian Stock Market. 

Instead of relying on rumors or subjective analysis, the platform combines strict mathematical modeling (based on SEBI allotment rules) with advanced Machine Learning (Gradient Boosting (Scikit-Learn `GradientBoostingClassifier` & `GradientBoostingRegressor`)) to predict listing gains and calculate exact allotment probabilities.

## 2. Core Pillars & Rules

### Rule 1: Strict SEBI Compliance
All mathematical calculations for IPO allotment must strictly follow SEBI's proportionate lottery guidelines. 
- Retail quotas are distributed based on a minimum lot size.
- Multiple applications from the same PAN must be mathematically treated as a single application (no probability increase).
- Maximum retail allotment is capped at 1 lot per PAN in oversubscribed issues.

### Rule 2: Data Integrity & Anti-Overfitting
- Machine Learning models must not be overfitted.
- We rely on high-quality academic datasets (e.g., from Hugging Face) merged with extensive historical scraping to ensure a diverse range of sectors and market conditions.
- Validation must use robust techniques like Leave-One-Out Cross-Validation (LOOCV).

### Rule 3: Graceful Web Scraping & Resilience
- Live data (GMP, subscriptions) is pulled dynamically via web scraping (e.g., IPO Watch).
- Scrapers must run in isolated background threads asynchronously so they *never* block the main API from serving user requests.
- Scraped data must be cached locally (e.g., `live_ipos.json`) to protect against network outages or cloudflare blocks.

### Rule 4: Credibility & "Proof of Work"
- The AI must not act like a black box. The UI must always show "Peer Comparisons"—comparing an active IPO to historical peers in the same sector and size bracket, alongside the AI's retroactive prediction vs the historical actual outcome.

---

## 3. The Build Plan (11 Stages)

### Phase 1: The Backend Brain (Completed)
- **Stage 1: Historical Data Sourcing [COMPLETED]**
  - Synthesized a robust dataset of 211 historical Indian IPOs spanning 12+ sectors.
- **Stage 2: SEBI Allotment Math Engine [COMPLETED]**
  - Built `calculator.py` to process PANs and compute precise lottery odds.
- **Stage 3: AI Model Training [COMPLETED]**
  - Trained dual Gradient Boosting (Scikit-Learn `GradientBoostingClassifier` & `GradientBoostingRegressor`) models (Regressor for exact %, Classifier for buckets) and saved them via `joblib`.
- **Stage 4: FastAPI Core [COMPLETED]**
  - Built the `main.py` server with strict Pydantic schemas exposing `/api/allotment-odds` and `/api/ipo/verdict`.
- **Stage 5: Live Data Scraper [COMPLETED]**
  - Built an automated `BeautifulSoup` scraper that wakes up every 15 minutes in the background, parses live Grey Market Premium data, and feeds the `/api/live-ipos` endpoint.
- **Stage 6: Peer Comparison System [COMPLETED]**
  - Built the "credibility-proof" engine (`/api/ipo/peers`) that scans historical data for similar companies and generates retroactive AI evaluations.

### Phase 2: The Frontend Face (Next)
- **Stage 7: Next.js Initialization & Theme**
  - Create a modern, responsive Next.js application with a premium "Hacker/Fintech" dark-mode aesthetic (TailwindCSS).
- **Stage 8: Live Market Dashboard**
  - Build the landing page showing a live ticker/grid of currently active IPOs fetched from our background scraper.
- **Stage 9: The Prediction Interface**
  - Build the interactive detail page where users can view an active IPO and trigger the XGBoost model to get a real-time listing gain verdict.
- **Stage 10: Allotment & Peer Credibility Views**
  - Integrate the SEBI odds calculator (with PAN input masking) and a visual "Comparables" table showing the historical peers.

### Phase 3: Deployment
- **Stage 11: Productionization**
  - Containerize the backend and frontend. Connect them safely. Deploy to a live environment (e.g., Vercel + Render).
