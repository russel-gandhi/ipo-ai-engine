"""
Deep dive into ipowatch detail page to understand which tables and
paragraphs belong to the target IPO vs related IPOs.
"""
import requests
from bs4 import BeautifulSoup
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Check Fusion Klassroom detail page
url = "https://ipowatch.in/fusion-klassroom-ipo/"
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

# Print ALL h1-h5 headings and their surrounding context
print("=" * 80)
print(f"DETAIL PAGE: {url}")
print("=" * 80)

print("\n--- ALL HEADINGS ---")
for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
    print(f"  [{h.name}] {h.text.strip()[:120]}")

# Find the main content area
# Usually the article/main content div
content = soup.find('article') or soup.find('main') or soup.find('div', class_='entry-content')
if content:
    print(f"\nFound main content container: {content.name}, class={content.get('class')}")
else:
    print("\nNo article/main/entry-content found, using full page")
    content = soup

# Show structure: heading -> tables -> paragraphs in order
print("\n--- CONTENT STRUCTURE (in order) ---")
for elem in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'table', 'p']):
    if elem.name.startswith('h'):
        print(f"\n  [{elem.name}] {elem.text.strip()[:100]}")
    elif elem.name == 'table':
        rows = elem.find_all('tr')
        first_row = [c.text.strip()[:40] for c in rows[0].find_all(['th','td'])] if rows else []
        print(f"  [TABLE {len(rows)} rows] Header: {first_row}")
    elif elem.name == 'p':
        text = elem.text.strip()
        if len(text) > 30:
            print(f"  [P] {text[:120]}...")

# Also check: does the page title match?
print(f"\n--- PAGE TITLE ---")
title = soup.find('title')
if title:
    print(f"  {title.text.strip()}")

# Check H1
h1 = soup.find('h1')
if h1:
    print(f"  H1: {h1.text.strip()}")
