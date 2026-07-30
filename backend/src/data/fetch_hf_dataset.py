import pandas as pd
from datasets import load_dataset
import numpy as np
import re

def standardize_sector(name):
    name = name.lower()
    if any(x in name for x in ['bank', 'finance', 'capital', 'fincap', 'wealth']):
        return 'Financial Services'
    if any(x in name for x in ['tech', 'software', 'info', 'cyber', 'data']):
        return 'Technology'
    if any(x in name for x in ['health', 'pharma', 'life', 'care', 'med']):
        return 'Healthcare'
    if any(x in name for x in ['infra', 'build', 'real estate', 'prop']):
        return 'Infrastructure'
    if any(x in name for x in ['steel', 'metal', 'auto', 'engine', 'motor', 'power']):
        return 'Manufacturing'
    if any(x in name for x in ['food', 'consumer', 'retail', 'mart']):
        return 'Consumer Goods'
    return 'Other'

def clean_subscription(val):
    if not val or pd.isna(val):
        return 0.0
    try:
        val = str(val).replace('x', '').replace(',', '').strip()
        return float(val)
    except:
        return 0.0

def clean_price(val):
    if not val or pd.isna(val):
        return 0.0
    try:
        # Extract number from strings like "₹38 per share" or "₹38.00"
        match = re.search(r'[\d\.]+', str(val))
        if match:
            return float(match.group())
        return 0.0
    except:
        return 0.0

def process_hf_dataset():
    print("Loading HF Dataset...")
    ds = load_dataset('Coder-Dragon/Indian-IPO-2006-2025')
    df = ds['train'].to_pandas()
    
    # Filter out SME and get mainboard (Issue Size > 50 Cr roughly)
    df['clean_issue_size'] = df['Issue Amount (Rs.cr.)'].apply(clean_price)
    df = df[df['clean_issue_size'] > 50]
    
    new_rows = []
    
    for idx, row in df.iterrows():
        company = str(row['Company']).replace(' IPO', '').strip()
        issue_price = clean_price(row['Issue Price'])
        listing_price = clean_price(row['Price Listing On'])
        
        if issue_price == 0 or listing_price == 0:
            continue
            
        listing_gain_pct = ((listing_price - issue_price) / issue_price) * 100
        
        # Bucket gain
        if listing_gain_pct < 0:
            bucket = 'loss'
        elif listing_gain_pct < 10:
            bucket = 'flat'
        elif listing_gain_pct < 40:
            bucket = 'moderate'
        else:
            bucket = 'high'
            
        sector = standardize_sector(company)
        
        sub_retail = clean_subscription(row['RII Subscription'])
        sub_nii = clean_subscription(row['NII Subscription'])
        sub_qib = clean_subscription(row['QIB Subscription'])
        sub_overall = clean_subscription(row['Total Subscription'])
        
        # Need some basic subs
        if sub_overall == 0:
            continue
            
        new_rows.append({
            'company': company,
            'sector': sector,
            'issue_size': row['clean_issue_size'],
            'fresh_vs_ofs_ratio': 0.5, # Imputed default
            'price_band': issue_price,
            'sub_retail': sub_retail,
            'sub_nii': sub_nii,
            'sub_qib': sub_qib,
            'sub_overall': sub_overall,
            'gmp_trend': 'flat', # Default imputed
            'actual_listing_gain_pct': round(listing_gain_pct, 2),
            'source_url': row['Ipo URL'],
            'listing_gain_bucket': bucket
        })
        
    new_df = pd.DataFrame(new_rows)
    print(f"Extracted {len(new_df)} valid mainboard rows from HF.")
    
    # Load existing CSV
    existing_df = pd.read_csv('backend/src/data/historical_ipos.csv')
    
    # Keep existing rows unconditionally
    existing_len = len(existing_df)
    needed = max(0, 120 - existing_len)
    
    if len(new_df) > needed:
        new_df = new_df.sample(needed, random_state=42)
        
    merged_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['company'], keep='first')
    
    merged_df.to_csv('backend/src/data/historical_ipos.csv', index=False)
    print(f"Updated historical_ipos.csv. Total rows: {len(merged_df)}")

if __name__ == "__main__":
    process_hf_dataset()
