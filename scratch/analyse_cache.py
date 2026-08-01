"""
Analyse cached ipowatch.in detail pages to answer the subscription question:
Are subscription multiples (QIB x / NII x / Retail x) present on detail pages?
"""
import json
import hashlib
import os
from bs4 import BeautifulSoup
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CACHE_DIR = os.path.join('backend', 'src', 'scraper', '.cache', 'details')
data = json.load(open(os.path.join('backend', 'src', 'data', 'live_ipos.json'), encoding='utf-8'))
ipos = data['ipos']

def url_to_cache_key(url):
    return hashlib.md5(url.encode()).hexdigest() + '.html'

# Check open/upcoming IPOs from cache
targets = [
    (i['name'], i.get('detail_url'))
    for i in ipos
    if i.get('detail_url') and i.get('status') in ('open', 'closing_today', 'upcoming')
][:5]

for name, url in targets:
    key = url_to_cache_key(url)
    path = os.path.join(CACHE_DIR, key)
    if not os.path.exists(path):
        print(f'NO CACHE: {name}')
        continue

    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    title = soup.find('title')
    title_text = title.text.strip()[:100] if title else 'N/A'

    print(f'=== {name} ===')
    print(f'  Page title: {title_text}')

    # All headings
    headings = soup.find_all(['h1', 'h2', 'h3'])
    print(f'  Headings ({len(headings)}):')
    for h in headings[:12]:
        print(f'    [{h.name}] {h.text.strip()[:80]}')

    # Subscription tables
    print('  Subscription-related tables:')
    found = False
    for i, tbl in enumerate(soup.find_all('table')):
        tbl_text = tbl.get_text().lower()
        if any(kw in tbl_text for kw in ['subscri', ' times', 'applied']):
            rows = tbl.find_all('tr')
            print(f'    TABLE[{i}] ({len(rows)} rows):')
            for r in rows[:8]:
                cells = [c.get_text().strip()[:45] for c in r.find_all(['th', 'td'])]
                print(f'      {cells}')
            found = True
    if not found:
        print('    (none found on this page)')

    # All table headers (to understand what tables exist)
    print('  All table first-rows:')
    for i, tbl in enumerate(soup.find_all('table')):
        rows = tbl.find_all('tr')
        if rows:
            cells = [c.get_text().strip()[:35] for c in rows[0].find_all(['th', 'td'])]
            print(f'    TABLE[{i}]: {cells}')

    print()
