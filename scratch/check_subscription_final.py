"""
Final check: Look at the full GMP table for ALL columns (some might have 
subscription data), and also check if ipowatch has a subscription status
table that loads via regular HTML (not JS).
"""
import requests
from bs4 import BeautifulSoup
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Step 1: Check if any ipowatch page has per-category subscription data
print("=" * 60)
print("CHECK 1: Full GMP table columns + any secondary tables")
print("=" * 60)

res = requests.get(
    'https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/',
    headers=headers
)
soup = BeautifulSoup(res.text, 'html.parser')
tables = soup.find_all('table')
print(f"Total tables on GMP page: {len(tables)}")

for ti, table in enumerate(tables):
    rows = table.find_all('tr')
    header_row = rows[0] if rows else None
    header_cols = [c.text.strip() for c in header_row.find_all(['th', 'td'])] if header_row else []
    print(f"\nTable {ti} - Header: {header_cols}")
    # Print a couple data rows
    for ri in range(1, min(3, len(rows))):
        cols = [c.text.strip().replace('\n', ' ')[:40] for c in rows[ri].find_all(['th', 'td'])]
        print(f"  Row {ri}: {cols}")

# Step 2: Check chittorgarh's free subscription total + category from the detail page carefully
print(f"\n{'=' * 60}")  
print("CHECK 2: Chittorgarh IPO list page for active IPOs")
print(f"{'=' * 60}")

try:
    # Try the "current IPOs" page
    curr_url = "https://www.chittorgarh.com/report/mainboard-ipo-list-in-india-bse-nse/83/"
    res2 = requests.get(curr_url, headers=headers, timeout=15)
    print(f"Mainboard list status: {res2.status_code}")
    
    if res2.status_code == 200:
        soup2 = BeautifulSoup(res2.text, 'html.parser')
        tables2 = soup2.find_all('table')
        print(f"Found {len(tables2)} tables")
        for ti, table in enumerate(tables2[:2]):
            rows = table.find_all('tr')
            print(f"\nTable {ti} ({len(rows)} rows):")
            for ri, row in enumerate(rows[:5]):
                cols = [c.text.strip().replace('\n', ' ')[:60] for c in row.find_all(['th', 'td'])]
                print(f"  R{ri}: {cols}")
except Exception as e:
    print(f"Error: {e}")

# Step 3: Try SME IPO page
print(f"\n{'=' * 60}")
print("CHECK 3: Chittorgarh SME list + subscription")
print(f"{'=' * 60}")

try:
    sme_url = "https://www.chittorgarh.com/report/sme-ipo-list-in-india-bse-sme-nse-emerge/84/"
    res3 = requests.get(sme_url, headers=headers, timeout=15)
    print(f"SME list status: {res3.status_code}")
    
    if res3.status_code == 200:
        soup3 = BeautifulSoup(res3.text, 'html.parser')
        tables3 = soup3.find_all('table')
        print(f"Found {len(tables3)} tables")
        for ti, table in enumerate(tables3[:2]):
            rows = table.find_all('tr')
            print(f"\nTable {ti} ({len(rows)} rows):")
            for ri, row in enumerate(rows[:5]):
                cols = [c.text.strip().replace('\n', ' ')[:60] for c in row.find_all(['th', 'td'])]
                print(f"  R{ri}: {cols}")
except Exception as e:
    print(f"Error: {e}")

# Step 4: Check if investorgain subscription page has data (it's a common source)
print(f"\n{'=' * 60}")
print("CHECK 4: Investorgain subscription status page variants")
print(f"{'=' * 60}")

try:
    # Try the specific subscription status page
    urls = [
        "https://www.investorgain.com/report/live-ipo-gmp/331/",
        "https://www.investorgain.com/report/ipo-subscription-status/336/",
    ]
    for url in urls:
        res4 = requests.get(url, headers=headers, timeout=15)
        soup4 = BeautifulSoup(res4.text, 'html.parser')
        tables4 = soup4.find_all('table')
        print(f"\n{url}")
        print(f"Status: {res4.status_code}, Tables: {len(tables4)}")
        for ti, table in enumerate(tables4[:2]):
            rows = table.find_all('tr')
            print(f"  Table {ti} ({len(rows)} rows):")
            for ri, row in enumerate(rows[:5]):
                cols = [c.text.strip().replace('\n', ' ')[:60] for c in row.find_all(['th', 'td'])]
                print(f"    R{ri}: {cols}")
except Exception as e:
    print(f"Error: {e}")
