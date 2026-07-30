import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

url = "https://www.investorgain.com/report/ipo-performance-tracker/323/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")
if tables:
    try:
        df = pd.read_html(StringIO(str(tables[0])))[0]
        print(df.columns)
        print(df.head(2))
    except Exception as e:
        print(e)
