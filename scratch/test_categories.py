import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)

print("--- Testing RETAIL ---")
res_retail = client.post("/api/allotment-odds", json={"category": "Retail", "sub_retail": 3.07, "num_pans": 2})
print(res_retail.status_code, res_retail.json()["probability_pct"], res_retail.json()["allotment_regime"])

print("\n--- Testing sHNI ---")
res_shni = client.post("/api/allotment-odds", json={"category": "sHNI", "sub_nii": 8.4, "applied_lots": 14})
print(res_shni.status_code, res_shni.json()["probability_pct"], res_shni.json()["min_allotment_value"])

print("\n--- Testing bHNI ---")
res_bhni = client.post("/api/allotment-odds", json={"category": "bHNI", "sub_nii": 8.4, "applied_lots": 68})
print(res_bhni.status_code, res_bhni.json()["expected_lots"], res_bhni.json()["allotment_ratio_str"])
