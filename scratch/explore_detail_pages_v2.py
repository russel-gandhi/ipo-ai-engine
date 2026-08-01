"""
Explore ipowatch.in detail page structure more thoroughly -
specifically looking for subscription data, about text, and how
to extract all the fields we need.
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

# Step 1: Get all IPO links + status from the GMP table
print("=" * 60)
print("STEP 1: GMP Table - all rows with links and status")
print("=" * 60)

res = requests.get(
    'https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/',
    headers=headers
)
soup = BeautifulSoup(res.text, 'html.parser')
tables = soup.find_all('table')

# Print full header
rows = tables[0].find_all('tr')
header_cols = [c.text.strip() for c in rows[0].find_all(['th', 'td'])]
print(f"Columns: {header_cols}")
print()

links_with_data = []
for row in rows[1:]:
    cols = row.find_all('td')
    if len(cols) >= 8:
        name = cols[0].text.strip()
        a_tag = cols[0].find('a')
        link = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
        gmp = cols[1].text.strip()
        trend = cols[2].text.strip()
        price = cols[3].text.strip()
        est_listing = cols[4].text.strip()
        date_col = cols[5].text.strip()
        type_col = cols[6].text.strip()
        status = cols[7].text.strip()
        
        print(f"  {name:35s} | GMP={gmp:6s} | Price={price:10s} | Status={status:15s} | Type={type_col} | Link={link}")
        if link:
            links_with_data.append({
                'name': name,
                'link': link,
                'status': status,
                'type': type_col,
                'date': date_col,
            })

# Step 2: Scrape a detail page for an OPEN IPO
open_ipos = [l for l in links_with_data if 'open' in l['status'].lower() or 'subscribe' in l['status'].lower()]
if not open_ipos:
    open_ipos = links_with_data[:1]

print(f"\n{'=' * 60}")
print(f"STEP 2: Detail page for '{open_ipos[0]['name']}' (status: {open_ipos[0]['status']})")
print(f"URL: {open_ipos[0]['link']}")
print(f"{'=' * 60}")

res2 = requests.get(open_ipos[0]['link'], headers=headers)
soup2 = BeautifulSoup(res2.text, 'html.parser')

# Print ALL headings
print("\n--- ALL HEADINGS ---")
for h in soup2.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
    print(f"  [{h.name}] {h.text.strip()[:120]}")

# Print ALL tables with FULL content
tables2 = soup2.find_all('table')
print(f"\n--- ALL TABLES ({len(tables2)} found) ---")
for ti, table in enumerate(tables2):
    rows = table.find_all('tr')
    print(f"\n  TABLE {ti} ({len(rows)} rows):")
    for ri, row in enumerate(rows):
        cols = [c.text.strip().replace('\n', ' ')[:80] for c in row.find_all(['th', 'td'])]
        print(f"    R{ri}: {cols}")

# Print key paragraphs
print(f"\n--- KEY PARAGRAPHS ---")
for pi, p in enumerate(soup2.find_all('p')):
    text = p.text.strip()
    if len(text) > 50:
        print(f"  P{pi} ({len(text)} chars): {text[:300]}")
        print()

# Step 3: Check if subscription data is on the detail page or a separate URL
print(f"\n{'=' * 60}")
print("STEP 3: Looking for subscription data patterns")
print(f"{'=' * 60}")

page_text = soup2.get_text().lower()
sub_patterns = ['subscription', 'subscribed', 'times', 'oversubscrib']
for pattern in sub_patterns:
    count = page_text.count(pattern)
    if count > 0:
        # Find context around first occurrence
        idx = page_text.find(pattern)
        context = page_text[max(0, idx-50):idx+100]
        print(f"  '{pattern}' found {count} times. Context: ...{context}...")
