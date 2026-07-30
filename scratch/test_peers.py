import requests
import json

base_url = "http://127.0.0.1:8000"

peer_payload = {
    "issue_size": 269.0, # Cr (Indo-MIM size)
    "sector": "Precision Engineering"
}

print("\n--- Testing Peer Comparison Endpoint ---")
try:
    res = requests.post(f"{base_url}/api/ipo/peers", json=peer_payload)
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print("Error:", e)
