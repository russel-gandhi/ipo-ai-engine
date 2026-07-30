import requests
import json

base_url = "http://127.0.0.1:8000"

print("\n--- 1. Testing Live Data Scraper (Stage 5) ---")
res = requests.get(f"{base_url}/api/live-ipos")
live_data = res.json()
print(f"Status: {res.status_code}")
print(f"Last Updated: {live_data['last_updated']}")
print(f"Total Live IPOs tracked: {len(live_data['ipos'])}")
# Print first two as an example
for ipo in live_data['ipos'][:2]:
    print(f"  -> {ipo['name']}: GMP = Rs.{ipo['gmp']}, Price Band = Rs.{ipo['price_band']}, Trend = {ipo['gmp_trend']}")

print("\n--- 2. Testing SEBI Allotment Odds (Stage 2 + 4) ---")
# Simulating Indo-MIM Retail Application (Assuming 150000 retail applications for 5M shares quota, minimum lot 100)
allotment_payload = {
    "pan": "ABCDE1234F",
    "category": "Retail",
    "applied_amount": 14500,
    "ipo_data": {
        "retail_shares_quota": 5000000,
        "retail_gross_applications": 150000, 
        "min_lot_shares_retail": 100
    }
}
res2 = requests.post(f"{base_url}/api/allotment-odds", json=allotment_payload)
print(f"Status: {res2.status_code}")
print(json.dumps(res2.json(), indent=2))

print("\n--- 3. Testing ML Verdict Predictor (Stage 3 + 4) ---")
# Simulating Indo-MIM stats
verdict_payload = {
    "issue_size": 269.0, # Cr
    "fresh_vs_ofs_ratio": 0.8,
    "sub_retail": 4.5,
    "sub_nii": 2.1,
    "sub_qib": 6.8,
    "sub_overall": 4.1,
    "price_band": 485,
    "sector": "Precision Engineering",
    "gmp_trend": "rising" # GMP is 187 currently
}
res3 = requests.post(f"{base_url}/api/ipo/verdict", json=verdict_payload)
print(f"Status: {res3.status_code}")
print(json.dumps(res3.json(), indent=2))
