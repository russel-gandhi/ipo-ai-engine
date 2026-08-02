import asyncio
import json
import os
import math
from datetime import datetime, timezone
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task to run scraper every 15 minutes
async def periodic_scraper():
    while True:
        # Run scraper in a thread to avoid blocking event loop
        await asyncio.to_thread(scrape_ipo_watch)
        await asyncio.sleep(900) # 15 minutes

def _maybe_refresh_stale_data():
    """Lazy refresh: re-scrape if cached data is older than 15 minutes."""
    live_file = os.path.join(os.path.dirname(__file__), 'data', 'live_ipos.json')
    if not os.path.exists(live_file):
        scrape_ipo_watch()
        return
    try:
        with open(live_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        last_updated = data.get("last_updated")
        if not last_updated:
            scrape_ipo_watch()
            return
        updated_at = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
        age_minutes = (datetime.now(timezone.utc) - updated_at).total_seconds() / 60
        if age_minutes > 15:
            scrape_ipo_watch()
    except Exception:
        pass

@app.on_event("startup")
async def startup_event():
    if os.getenv("ENABLE_BACKGROUND_SCRAPER", "true").lower() == "true":
        asyncio.create_task(periodic_scraper())

@app.get("/api/live-ipos")
def get_live_ipos(name: str = None):
    try:
        _maybe_refresh_stale_data()
        live_file = os.path.join(os.path.dirname(__file__), 'data', 'live_ipos.json')
        if not os.path.exists(live_file):
            return {"last_updated": None, "ipos": []}
        with open(live_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if name:
            data["ipos"] = [
                ipo for ipo in data.get("ipos", [])
                if name.lower() in ipo.get("name", "").lower()
            ]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/")
def read_root():
    return {"message": "IPO Insight API is running"}

@app.post("/api/allotment-odds")
def get_allotment_odds(request: AllotmentRequest):
    try:
        payload = request.model_dump()
        if request.ipo_data:
            payload["ipo_data"] = request.ipo_data.model_dump()
        response = calculate_allotment_engine(payload)
        
        # Maintain backward compatible dict format if older frontend expects it
        res_dict = response.model_dump()
        res_dict["odds_per_pan"] = round((response.probability_pct or 0.0) / 100.0, 4)
        return res_dict
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Allotment error: {str(e)}")

@app.post("/api/ipo/calculate-allotment")
def calculate_allotment_enriched(request: Dict[str, Any]):
    try:
        return calculate_allotment_engine(request).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Allotment engine error: {str(e)}")

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
            walk_forward_accuracy_for_bucket=result["walk_forward_accuracy_for_bucket"],
            model_agreement=result["model_agreement"],
            disclaimer=result["disclaimer"]
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/api/ipo/peers", response_model=PeerComparisonResponse)
def get_ipo_peers(request: PeerComparisonRequest):
    try:
        peers_result = find_comparable_peers(
            target_sector=request.sector,
            target_issue_size=request.issue_size,
            top_n=5
        )
        return PeerComparisonResponse(
            target_sector=request.sector,
            target_issue_size=request.issue_size,
            peer_hit_rate=peers_result["peer_hit_rate"],
            peers=peers_result["peers"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Peer lookup error: {str(e)}")
