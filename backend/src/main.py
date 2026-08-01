import asyncio
import json
import os
import math
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

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_scraper())

@app.get("/api/live-ipos")
def get_live_ipos(name: str = None):
    try:
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

@app.post("/api/allotment-odds", response_model=AllotmentResponse)
def get_allotment_odds(request: AllotmentRequest):
    try:
        # Case A: Detailed IPO Data dictionary provided
        if request.ipo_data is not None:
            result = calculate_sebi_allotment_odds(
                pan=request.pan or "ABCDE1234F",
                category=request.category or "Retail",
                applied_amount=request.applied_amount or 15000.0,
                ipo_data=request.ipo_data.model_dump()
            )
            if "error" in result:
                raise ValueError(result["error"])

            prob_pct = result["probability_pct"]
            p_single = prob_pct / 100.0
            n_pans = request.num_pans or 1
            p_at_least_one = 1.0 - math.pow(1.0 - p_single, n_pans) if p_single < 1.0 else 1.0

            return AllotmentResponse(
                category=result["category"],
                masked_pan=result["masked_pan"],
                probability_pct=prob_pct,
                probability_at_least_one_lot=round(p_at_least_one, 4),
                odds_per_pan=round(p_single, 4),
                expected_lots=round(n_pans * p_single, 2),
                allotment_regime="Proportionate Lottery" if prob_pct < 100.0 else "Full Allotment",
                explain_text=result["explain_text"],
                guardrail=result["guardrail"],
                privacy_note=result["privacy_note"]
            )

        # Case B: Interactive calculator parameters (sub_retail, num_pans, etc.)
        sub_retail = request.sub_retail if request.sub_retail is not None else 3.07
        n_pans = request.num_pans if request.num_pans is not None else 1

        if sub_retail <= 1.0:
            p_single = 1.0
            allotment_regime = "Full Allotment"
            guardrail_msg = "Subscription is less than 1.0x — all valid applicants receive full allotment."
        else:
            # SEBI lottery rule: 1 lot per PAN draw probability = 1 / sub_retail
            p_single = min(1.0, 1.0 / sub_retail)
            allotment_regime = "Proportionate Lottery"
            guardrail_msg = "Applying for multiple lots on the same PAN does NOT increase your allotment probability. Submitting 1 lot per PAN across distinct family PANs is the optimal strategy."

        prob_pct = round(p_single * 100.0, 2)
        p_at_least_one = round(1.0 - math.pow(1.0 - p_single, n_pans), 4) if p_single < 1.0 else 1.0
        expected_lots = round(n_pans * p_single, 2)

        explain_text = (
            f"With Retail category subscribed {sub_retail:.2f}x, each PAN has a {prob_pct:.1f}% chance of allotment. "
            f"Submitting across {n_pans} family PAN(s) gives a {round(p_at_least_one * 100, 1)}% probability of winning at least 1 lot."
        )

        return AllotmentResponse(
            category=request.category or "Retail",
            masked_pan="⁕⁕⁕⁕⁕⁕1234F",
            probability_pct=prob_pct,
            probability_at_least_one_lot=p_at_least_one,
            odds_per_pan=round(p_single, 4),
            expected_lots=expected_lots,
            allotment_regime=allotment_regime,
            explain_text=explain_text,
            guardrail=guardrail_msg,
            privacy_note="PAN data lives strictly in volatile memory and is never written to persistent storage."
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Allotment error: {str(e)}")

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
