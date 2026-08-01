"""
Check subscription data sources - ipowatch subscription status page 
and chittorgarh subscription page.
"""
import requests
from bs4 import BeautifulSoup
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Try chittorgarh subscription status page pattern
print("=" * 60)
print("CHECK 1: Chittorgarh Subscription Status")
print("=" * 60)

# Chittorgarh has a subscription status page for each IPO
# Pattern: https://www.chittorgarh.com/ipo/xxx-ipo/XXXX/
# Let's search for a current one first
try:
    # Check the main IPO subscription page  
    sub_url = "https://www.chittorgarh.com/report/ipo-subscription-status-live-bidding-data/746/"
    res = requests.get(sub_url, headers=headers, timeout=15)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        if tables:
            rows = tables[0].find_all('tr')
            print(f"\nTable 0 ({len(rows)} rows):")
            for ri, row in enumerate(rows[:10]):
                cols = [c.text.strip().replace('\n', ' ')[:60] for c in row.find_all(['th', 'td'])]
                print(f"  R{ri}: {cols}")
except Exception as e:
    print(f"Error: {e}")

# Check ipowatch subscription status pattern 
print(f"\n{'=' * 60}")
print("CHECK 2: ipowatch.in subscription status page")
print(f"{'=' * 60}")

# ipowatch has subscription pages like /ipo-subscription-status/
try:
    sub_url2 = "https://ipowatch.in/ipo-subscription-status/"
    res2 = requests.get(sub_url2, headers=headers, timeout=15)
    print(f"Status: {res2.status_code}")
    
    if res2.status_code == 200:
        soup2 = BeautifulSoup(res2.text, 'html.parser')
        tables2 = soup2.find_all('table')
        print(f"Found {len(tables2)} tables")
        
        for ti, table in enumerate(tables2[:3]):
            rows = table.find_all('tr')
            print(f"\nTable {ti} ({len(rows)} rows):")
            for ri, row in enumerate(rows[:15]):
                cols = [c.text.strip().replace('\n', ' ')[:60] for c in row.find_all(['th', 'td'])]
                print(f"  R{ri}: {cols}")
except Exception as e:
    print(f"Error: {e}")

# Check if ipowatch detail page has subscription data
print(f"\n{'=' * 60}")
print("CHECK 3: Does ipowatch detail page have subscription data?")
print(f"{'=' * 60}")

# Get the first IPO link from the GMP table
res_gmp = requests.get(
    'https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/',
    headers=headers
)
soup_gmp = BeautifulSoup(res_gmp.text, 'html.parser')
gmp_table = soup_gmp.find_all('table')[0]
gmp_rows = gmp_table.find_all('tr')

# Find an IPO with "Open" status
for row in gmp_rows[1:]:
    cols = row.find_all('td')
    if len(cols) >= 8:
        status = cols[7].text.strip().lower()
        if 'open' in status or 'subscrib' in status:
            a_tag = cols[0].find('a')
            if a_tag:
                name = cols[0].text.strip()
                link = a_tag['href']
                print(f"Found open IPO: {name} at {link}")
                
                res3 = requests.get(link, headers=headers, timeout=15)
                soup3 = BeautifulSoup(res3.text, 'html.parser')
                
                # Search for subscription-related tables
                tables3 = soup3.find_all('table')
                for ti, table in enumerate(tables3):
                    table_text = table.get_text().lower()
                    if any(k in table_text for k in ['subscription', 'qib', 'nii', 'retail', 'times']):
                        rows = table.find_all('tr')
                        print(f"\n  MATCH Table {ti} ({len(rows)} rows):")
                        for ri, row in enumerate(rows):
                            cols_text = [c.text.strip().replace('\n', ' ')[:60] for c in row.find_all(['th', 'td'])]
                            print(f"    R{ri}: {cols_text}")
                
                break
