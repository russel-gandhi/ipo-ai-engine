import pandas as pd
import os
from typing import List, Dict
from backend.src.model.predict import predict_listing_gain

def find_comparable_peers(target_sector: str, target_issue_size: float, top_n: int = 5) -> List[Dict]:
    """
    Finds historical IPOs comparable to the target IPO based on sector and issue size.
    Computes retroactive AI predictions for each peer.
    """
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'historical_ipos.csv')
    df = pd.read_csv(csv_path)
    
    # 1. Filter by Sector
    sector_peers = df[df['sector'].str.lower() == target_sector.lower()].copy()
    
    if len(sector_peers) == 0:
        # Fallback: If no exact sector match, find peers by issue size (e.g. +/- 50%)
        min_size = target_issue_size * 0.5
        max_size = target_issue_size * 1.5
        peers = df[(df['issue_size'] >= min_size) & (df['issue_size'] <= max_size)].copy()
        similarity_msg = "Similar Size Bracket"
    else:
        peers = sector_peers
        similarity_msg = "Same Sector"
        
    if len(peers) == 0:
        # Extreme fallback: just find the closest by issue size overall
        peers = df.copy()
        similarity_msg = "Closest by Issue Size"
        
    # 2. Sort by absolute difference in issue size
    peers['size_diff'] = abs(peers['issue_size'] - target_issue_size)
    peers = peers.sort_values(by='size_diff').head(top_n)
    
    # 3. Generate retroactive predictions for the chosen peers
    results = []
    
    for _, row in peers.iterrows():
        # Build feature dict for the model
        features = {
            "issue_size": row['issue_size'],
            "sub_retail": row['sub_retail'],
            "sub_nii": row['sub_nii'],
            "sub_qib": row['sub_qib'],
            "sub_overall": row['sub_overall'],
            "price_band": row['price_band'],
            "fresh_vs_ofs_ratio": row['fresh_vs_ofs_ratio'],
            "sector": row['sector'],
            "gmp_trend": row['gmp_trend']
        }
        
        try:
            pred_result = predict_listing_gain(features)
            predicted_gain = pred_result['predicted_gain_pct']
        except Exception:
            predicted_gain = 0.0
            
        results.append({
            "company_name": row.get('company', 'Unknown IPO'),
            "sector": row['sector'],
            "issue_size": float(row['issue_size']),
            "actual_listing_gain_pct": float(row['actual_listing_gain_pct']),
            "predicted_gain_pct": predicted_gain,
            "similarity_score": similarity_msg
        })
        
    return results
