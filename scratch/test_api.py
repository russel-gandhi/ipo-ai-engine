import requests

allotment_data = {
    "pan": "ABCDE1234F",
    "category": "Retail",
    "applied_amount": 14900,
    "ipo_data": {
        "retail_shares_quota": 3500000,
        "retail_gross_applications": 200000,
        "min_lot_shares_retail": 100
    }
}
res = requests.post("http://127.0.0.1:8000/api/allotment-odds", json=allotment_data)
print("Allotment Response:", res.status_code, res.json())

# Test Verdict Endpoint
verdict_data = {
    "issue_size": 200,
    "fresh_vs_ofs_ratio": 0.8,
    "sub_retail": 10.5,
    "sub_nii": 5.0,
    "sub_qib": 20.0,
    "sub_overall": 12.0,
    "price_band": 150,
    "sector": "Technology",
    "gmp_trend": "rising"
}
res = requests.post("http://127.0.0.1:8000/api/ipo/verdict", json=verdict_data)
print("Verdict Response:", res.status_code, res.json())
