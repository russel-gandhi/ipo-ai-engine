"""
Get the full GMP table with all data to understand what fields
we can extract directly from the listing page vs. the detail page.
"""
import requests
from bs4 import BeautifulSoup
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

res = requests.get(
    'https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/',
    headers=headers
)
soup = BeautifulSoup(res.text, 'html.parser')
table = soup.find_all('table')[0]
rows = table.find_all('tr')

print("FULL GMP TABLE DATA:")
print("-" * 120)
for ri, row in enumerate(rows):
    cols = row.find_all(['th', 'td'])
    data = []
    for c in cols:
        text = c.text.strip().replace('\n', ' ')
        a = c.find('a')
        link = a['href'] if a and 'href' in a.attrs else ''
        data.append(f"{text} [{link}]" if link else text)
    print(f"R{ri:2d}: {data}")

print(f"\nTotal IPOs: {len(rows) - 1}")
