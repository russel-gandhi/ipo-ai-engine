import requests
import pandas as pd

url = "https://www.investorgain.com/report/live-ipo-gmp/331/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
resp = requests.get(url, headers=headers)
try:
    tables = pd.read_html(resp.content)
    print("Found tables:", len(tables))
    if len(tables) > 0:
        print(tables[0].head())
        tables[0].to_csv("test_investorgain.csv", index=False)
except Exception as e:
    print("Error:", e)
