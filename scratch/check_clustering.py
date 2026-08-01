import pandas as pd
import os

def check_clustering():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'data', 'historical_ipos.csv')
    df = pd.read_csv(csv_path)
    df_real = df[df['data_source'] == 'real_scraped'].copy()
    df_real['listing_date'] = pd.to_datetime(df_real['listing_date'])
    df_real['year'] = df_real['listing_date'].dt.year
    
    # Check sector distribution per year
    pivot = pd.crosstab(df_real['sector'], df_real['year'])
    
    report_path = os.path.join(os.path.dirname(__file__), 'clustering_report.txt')
    with open(report_path, 'w') as f:
        f.write("=== Sector x Year Distribution (real_scraped) ===\n")
        f.write(pivot.to_string())
        
    print(f"Saved clustering report to {report_path}")
    print(pivot)

if __name__ == "__main__":
    check_clustering()
