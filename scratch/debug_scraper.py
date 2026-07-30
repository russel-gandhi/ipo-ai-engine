import requests
from bs4 import BeautifulSoup
import traceback

res = requests.get('https://ipowatch.in/manipal-health-ipo/', headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(res.text, 'html.parser')

tables = soup.find_all('table')
print(f"Found {len(tables)} tables")
for table in tables:
    rows = table.find_all('tr')
    for row in rows:
        try:
            cols = [c.text.strip().replace('\u20b9', '') for c in row.find_all(['th', 'td'])]
            if len(cols) >= 2:
                key = cols[0].lower()
                val = cols[1].lower()
                if 'industry' in key or 'issue size' in key:
                    print(f"Match: {key} -> {val}")
        except Exception as e:
            pass
