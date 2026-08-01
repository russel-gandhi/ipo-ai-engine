import pandas as pd
import os
from typing import List, Dict
from backend.src.model.predict import predict_retroactive

def find_comparable_peers(target_sector: str, target_issue_size: float, top_n: int = 5) -> Dict:
    """
    Finds historical IPOs comparable to the target IPO based on sector and issue size.
    Computes retroactive AI predictions for each peer.
    """
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'historical_ipos.csv')
    df = pd.read_csv(csv_path)
    
    # 1. Filter by Sector
    sector_peers = df[df['sector'].str.lower() == target_sector.lower()].copy()
    
    if len(sector_peers) == 0:
        min_size = target_issue_size * 0.5
        max_size = target_issue_size * 1.5
        peers = df[(df['issue_size'] >= min_size) & (df['issue_size'] <= max_size)].copy()
        similarity_msg = "Similar Size Bracket"
    else:
        peers = sector_peers
        similarity_msg = "Same Sector"
        
    if len(peers) == 0:
        peers = df.copy()
        similarity_msg = "Closest by Issue Size"
        
    # 2. Sort by absolute difference in issue size
    peers['size_diff'] = abs(peers['issue_size'] - target_issue_size)
    peers = peers.sort_values(by='size_diff').head(top_n)
    
    # 3. Generate retroactive predictions for the chosen peers
    results = []
    hit_count = 0
    total_count = 0
    
    for _, row in peers.iterrows():
        features = {
            "issue_size": row['issue_size'],
            "sub_retail": row['sub_retail'],
            "sub_nii": row['sub_nii'],
            "sub_qib": row['sub_qib'],
            "sub_overall": row['sub_overall'],
            "price_band": row['price_band'],
            "fresh_vs_ofs_ratio": row['fresh_vs_ofs_ratio'],
            "sector": row['sector'],
            "gmp_trend": row['gmp_trend'],
            "anchor_allocation_pct": row.get('anchor_allocation_pct', 0.0),
            "gmp_trajectory": row.get('gmp_trajectory', 0.0),
            "market_regime_nifty_30d": row.get('market_regime_nifty_30d', 0.0),
            "is_sme": row.get('is_sme', False)
        }
        
        cutoff_date = row['listing_date']
        is_real = row.get('data_source', '') == 'real_scraped'
        
        try:
            pred_result = predict_retroactive(features, cutoff_date)
            retro_bucket = pred_result['bucket_estimate']
            retro_range = pred_result['historical_gain_range']
            retro_conf = pred_result['confidence_score']
            midpoint = pred_result.get('predicted_midpoint', 0.0)
        except Exception as e:
            retro_bucket = "N/A"
            retro_range = "N/A"
            retro_conf = "Error computing retroactive prediction"
            midpoint = 0.0
            
        actual_gain = float(row['actual_listing_gain_pct'])
        delta = round(midpoint - actual_gain, 1)
        
        # Check regime warning
        listing_dt = pd.to_datetime(cutoff_date)
        bull_start = pd.to_datetime("2021-03-01")
        bull_end = pd.to_datetime("2021-09-30")
        regime_warning = bool(bull_start <= listing_dt <= bull_end)
        
        if is_real and retro_bucket != "N/A":
            total_count += 1
            if abs(delta) <= 15.0:
                hit_count += 1
                
        results.append({
            "company_name": row.get('company', 'Unknown IPO'),
            "sector": row['sector'],
            "issue_size": float(row['issue_size']),
            "sub_overall": float(row['sub_overall']),
            "gmp_at_close": str(row.get('gmp_trend', 'N/A')),
            "actual_listing_gain_pct": actual_gain,
            "retroactive_bucket_estimate": retro_bucket,
            "retroactive_gain_range": retro_range,
            "delta": delta,
            "retroactive_confidence_score": retro_conf,
            "regime_warning": regime_warning,
            "similarity_score": similarity_msg
        })
        
    hit_rate_str = f"Model was within ±15% of actual listing gain in {hit_count} out of {total_count} similar past IPOs." if total_count > 0 else "Insufficient historical data for hit rate."
        
    return {
        "peer_hit_rate": hit_rate_str,
        "peers": results
    }
