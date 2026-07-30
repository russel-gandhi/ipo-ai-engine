import requests
import json

url = "http://127.0.0.1:8000/api/ipo/verdict"
payload = {
    "issue_size": 250.0,
    "fresh_vs_ofs_ratio": 1.0,
    "sub_retail": 12.5,
    "sub_nii": 45.2,
    "sub_qib": 110.0,
    "sub_overall": 55.0,
    "price_band": 350.0,
    "sector": "Healthcare",
    "gmp_trend": "rising",
    "is_sme": False,
    "anchor_allocation_pct": 30.0,
    "relative_issue_size": 1.2,
    "gmp_trajectory": 2.5,
    "market_regime_nifty_30d": 4.5
}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=payload, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
