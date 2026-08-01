import pandas as pd
import os
import numpy as np

def update_dataset():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'data')
    old_path = os.path.join(data_dir, 'historical_ipos.csv')
    new_path = os.path.join(data_dir, 'historical_ipos_new.csv')
    
    if not os.path.exists(new_path):
        print("Scraped data not found.")
        return
        
    df_old = pd.read_csv(old_path)
    df_synthetic = df_old[df_old['data_source'] == 'synthetic_interpolated'].copy()
    
    df_new = pd.read_csv(new_path)
    
    # Assign listing gain buckets based on actual_listing_gain_pct
    def assign_bucket(gain):
        if gain < 0: return 'loss'
        elif 0 <= gain < 15: return 'flat'
        elif 15 <= gain < 40: return 'moderate'
        else: return 'high'
        
    df_new['listing_gain_bucket'] = df_new['actual_listing_gain_pct'].apply(assign_bucket)
    
    df_final = pd.concat([df_new, df_synthetic], ignore_index=True)
    df_final.to_csv(old_path, index=False)
    
    # Generate coverage report
    df_real = df_final[df_final['data_source'] == 'real_scraped'].copy()
    df_real['year'] = pd.to_datetime(df_real['listing_date']).dt.year
    pivot = pd.crosstab([df_real['sector'], df_real['is_sme']], df_real['year'])
    
    report_path = os.path.join(os.path.dirname(__file__), 'coverage_report.txt')
    with open(report_path, 'w') as f:
        f.write("=== Coverage Report: Sector x SME x Year ===\n")
        f.write(pivot.to_string())
        
    print(f"Dataset updated. Wrote {len(df_final)} total rows to {old_path}")
    print(f"Coverage report written to {report_path}")

if __name__ == "__main__":
    update_dataset()
