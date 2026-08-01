import requests
import pandas as pd
from bs4 import BeautifulSoup
import io

url = "https://www.chittorgarh.com/report/mainboard-ipo-list-in-india-bse-nse/83/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")
if tables:
    try:
        df = pd.read_html(io.StringIO(str(tables[0])))[0]
        print(df.columns)
        print(df.head(2))
        print("Total rows:", len(df))
    except Exception as e:
        print(e)
