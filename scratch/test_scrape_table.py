import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}
url = "https://www.chittorgarh.com/report/mainboard-ipo-list-in-india-bse-nse/82/"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")
if len(tables) > 0:
    df = pd.read_html(StringIO(str(tables[0])))[0]
    print(df.columns)
    print(df.head(2))
