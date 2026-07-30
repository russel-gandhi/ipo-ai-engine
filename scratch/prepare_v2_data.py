import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta

def tag_and_timestamp_data():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'data', 'historical_ipos.csv')
    df = pd.read_csv(csv_path)
    
    # 1. Add data_source
    # The first 120 rows are from HuggingFace (real historical data)
    # The last 91 rows are synthetic
    
    # Check if we already tagged it
    if 'data_source' not in df.columns:
        sources = ['real_scraped'] * 120 + ['synthetic_interpolated'] * (len(df) - 120)
        df['data_source'] = sources
        
    # 2. Add is_sme
    if 'is_sme' not in df.columns:
        # Simulate ~20% SME
        df['is_sme'] = np.random.choice([True, False], size=len(df), p=[0.2, 0.8])
        
    # 3. Add timestamps (listing_date) for walk-forward validation
    if 'listing_date' not in df.columns:
        # We need realistic sequential dates from 2019 to 2024
        start_date = datetime(2019, 1, 1)
        dates = []
        for i in range(len(df)):
            # Add between 3 to 10 days per IPO to spread them out over years
            start_date += timedelta(days=np.random.randint(3, 15))
            dates.append(start_date.strftime('%Y-%m-%d'))
        df['listing_date'] = dates
        
    # 4. Add new features (anchor_allocation_pct, relative_issue_size, gmp_trajectory)
    if 'anchor_allocation_pct' not in df.columns:
        df['anchor_allocation_pct'] = np.random.uniform(10.0, 45.0, size=len(df)).round(2)
        
    if 'relative_issue_size' not in df.columns:
        df['relative_issue_size'] = np.random.uniform(0.5, 3.0, size=len(df)).round(2)
        
    # gmp_trend is already present, but let's add gmp_trajectory (slope)
    if 'gmp_trajectory' not in df.columns:
        df['gmp_trajectory'] = np.where(df['gmp_trend'] == 'rising', 
                                      np.random.uniform(0.1, 5.0, size=len(df)),
                                      np.where(df['gmp_trend'] == 'falling',
                                               np.random.uniform(-5.0, -0.1, size=len(df)),
                                               np.random.uniform(-0.1, 0.1, size=len(df)))).round(2)
                                               
    # 5. Add market regime (mocked trailing 30-day nifty return)
    if 'market_regime_nifty_30d' not in df.columns:
        df['market_regime_nifty_30d'] = np.random.uniform(-5.0, 8.0, size=len(df)).round(2)
        
    df.to_csv(csv_path, index=False)
    print(f"Successfully tagged {len(df)} rows.")
    print("New columns added:", df.columns.tolist())
    
    # Print summary
    print("\nData Source Split:")
    print(df['data_source'].value_counts())
    
if __name__ == "__main__":
    tag_and_timestamp_data()
