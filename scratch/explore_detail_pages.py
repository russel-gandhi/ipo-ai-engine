"""
Explore ipowatch.in detail page structure to understand
what data fields are available for scraping.
"""
import requests
from bs4 import BeautifulSoup
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Step 1: Get IPO links from the GMP table
print("=" * 60)
print("STEP 1: Getting IPO links from GMP table")
print("=" * 60)

res = requests.get(
    'https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/',
    headers=headers
)
soup = BeautifulSoup(res.text, 'html.parser')
tables = soup.find_all('table')

links = []
rows = tables[0].find_all('tr')
for row in rows[1:5]:  # First 4 IPOs
    cols = row.find_all('td')
    name = cols[0].text.strip() if cols else "?"
    a_tag = cols[0].find('a') if cols else None
    link = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
    status = cols[7].text.strip() if len(cols) > 7 else "?"
    print(f"  {name} -> {link} [{status}]")
    if link:
        links.append((name, link))

# Step 2: Scrape a detail page and dump ALL tables
if links:
    name, url = links[0]
    print(f"\n{'=' * 60}")
    print(f"STEP 2: Detail page for '{name}'")
    print(f"URL: {url}")
    print(f"{'=' * 60}")
    
    res2 = requests.get(url, headers=headers)
    soup2 = BeautifulSoup(res2.text, 'html.parser')
    
    # Print all headings
    print("\n--- HEADINGS ---")
    for h in soup2.find_all(['h1', 'h2', 'h3', 'h4']):
        print(f"  [{h.name}] {h.text.strip()[:100]}")
    
    # Print all tables with their content
    tables2 = soup2.find_all('table')
    print(f"\n--- TABLES ({len(tables2)} found) ---")
    for ti, table in enumerate(tables2):
        rows = table.find_all('tr')
        print(f"\n  TABLE {ti} ({len(rows)} rows):")
        for ri, row in enumerate(rows[:15]):  # First 15 rows
            cols = [c.text.strip().replace('\n', ' ')[:60] for c in row.find_all(['th', 'td'])]
            print(f"    R{ri}: {cols}")
    
    # Look for paragraphs that might contain "about" text
    print(f"\n--- PARAGRAPHS (first 500 chars each) ---")
    for pi, p in enumerate(soup2.find_all('p')[:10]):
        text = p.text.strip()
        if len(text) > 30:
            print(f"  P{pi}: {text[:200]}...")

# Step 3: Also check the subscription page pattern
print(f"\n{'=' * 60}")
print("STEP 3: Checking subscription page pattern")
print(f"{'=' * 60}")

# Try chittorgarh for H.R. Hygiene specifically
try:
    chittorgarh_url = "https://www.chittorgarh.com/ipo/hr-hygiene-products-ipo/2037/"
    res3 = requests.get(chittorgarh_url, headers=headers)
    print(f"Chittorgarh status: {res3.status_code}")
    if res3.status_code == 200:
        soup3 = BeautifulSoup(res3.text, 'html.parser')
        tables3 = soup3.find_all('table')
        print(f"Found {len(tables3)} tables")
        for ti, table in enumerate(tables3[:5]):
            rows = table.find_all('tr')
            print(f"\n  TABLE {ti} ({len(rows)} rows):")
            for ri, row in enumerate(rows[:10]):
                cols = [c.text.strip().replace('\n', ' ')[:60] for c in row.find_all(['th', 'td'])]
                print(f"    R{ri}: {cols}")
    else:
        print(f"  Chittorgarh returned {res3.status_code} - may need different URL")
except Exception as e:
    print(f"  Chittorgarh error: {e}")
