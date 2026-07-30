import asyncio
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.src.api.schemas import (
    AllotmentRequest, AllotmentResponse, 
    VerdictRequest, VerdictResponse,
    PeerComparisonRequest, PeerComparisonResponse
)
from backend.src.allotment.calculator import calculate_sebi_allotment_odds
from backend.src.model.predict import predict_listing_gain
from backend.src.scraper.refresh_job import scrape_ipo_watch
from backend.src.model.peers import find_comparable_peers

app = FastAPI(
    title="IPO Insight SEBI API",
    description="A SEBI-compliant IPO analysis and allotment probability API.",
    version="1.0.0"
)

# Background task to run scraper every 15 minutes
async def periodic_scraper():
    while True:
        # Run scraper in a thread to avoid blocking event loop
        await asyncio.to_thread(scrape_ipo_watch)
        await asyncio.sleep(900) # 15 minutes

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_scraper())

@app.get("/api/live-ipos")
def get_live_ipos():
    try:
        live_file = os.path.join(os.path.dirname(__file__), 'data', 'live_ipos.json')
        if not os.path.exists(live_file):
            return {"last_updated": None, "ipos": []}
        with open(live_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development; restrict to frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "IPO Insight API is running"}

@app.post("/api/allotment-odds", response_model=AllotmentResponse)
def get_allotment_odds(request: AllotmentRequest):
    try:
        result = calculate_sebi_allotment_odds(
            pan=request.pan,
            category=request.category,
            applied_amount=request.applied_amount,
            ipo_data=request.ipo_data.model_dump()
        )
        if "error" in result:
            raise ValueError(result["error"])
            
        return AllotmentResponse(
            category=result["category"],
            masked_pan=result["masked_pan"],
            probability_pct=result["probability_pct"],
            explain_text=result["explain_text"],
            guardrail=result["guardrail"],
            privacy_note=result["privacy_note"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/api/ipo/verdict", response_model=VerdictResponse)
def get_ipo_verdict(request: VerdictRequest):
    try:
        features = request.model_dump()
        result = predict_listing_gain(features)
        
        return VerdictResponse(
            bucket_estimate=result["bucket_estimate"],
            historical_gain_range=result["historical_gain_range"],
            confidence_score=result["confidence_score"],
            real_peer_count=result["real_peer_count"],
            total_peer_count=result["total_peer_count"],
            disclaimer=result["disclaimer"]
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/api/ipo/peers", response_model=PeerComparisonResponse)
def get_ipo_peers(request: PeerComparisonRequest):
    try:
        peers_list = find_comparable_peers(
            target_sector=request.sector,
            target_issue_size=request.issue_size,
            top_n=5
        )
        return PeerComparisonResponse(
            target_sector=request.sector,
            target_issue_size=request.issue_size,
            peers=peers_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Peer lookup error: {str(e)}")
