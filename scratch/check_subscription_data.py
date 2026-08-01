"""
Specifically check whether ipowatch.in detail pages contain subscription
multiples (QIB x / NII x / Retail x), and if so, where.

Also checks whether there's a separate subscription-status page.

Run this against a currently-open IPO.
"""
import requests
from bs4 import BeautifulSoup
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Test with open IPOs — try multiple to be sure
test_ipos = [
    ("Juniper Green Energy", "https://ipowatch.in/juniper-green-energy-ipo/"),
    ("MV Electrosystems", "https://ipowatch.in/mv-electrosystems-ipo/"),
    ("H.R. Hygiene Products", "https://ipowatch.in/h-r-hygiene-products-ipo/"),
]

SUBSCRIPTION_KEYWORDS = [
    'times', 'subscribed', 'subscription', 'x times', 'qib', 'nii', 'retail'
]

for ipo_name, url in test_ipos:
    print("=" * 70)
    print(f"IPO: {ipo_name}")
    print(f"URL: {url}")
    print("=" * 70)
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        print(f"HTTP Status: {res.status_code}")
        
        if res.status_code != 200:
            print("  FAILED — skipping")
            continue
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # --- Check 1: Look for subscription tables ---
        print("\n--- SUBSCRIPTION TABLE SEARCH ---")
        found_sub = False
        for i, table in enumerate(soup.find_all('table')):
            text = table.get_text().lower()
            if any(kw in text for kw in ['times', 'subscribed', 'subscription status']):
                rows = table.find_all('tr')
                print(f"  [TABLE {i}, {len(rows)} rows] CONTAINS SUBSCRIPTION DATA:")
                for row in rows[:8]:
                    cells = [c.get_text().strip()[:50] for c in row.find_all(['th', 'td'])]
                    print(f"    {cells}")
                found_sub = True
        
        if not found_sub:
            print("  No subscription table found on detail page.")
        
        # --- Check 2: Any text mentioning subscription multiples ---
        print("\n--- SUBSCRIPTION MENTIONS IN TEXT ---")
        sub_pattern = re.compile(r'\b(\d+\.?\d*)\s*x\b|\b(\d+\.?\d*)\s*times\b', re.IGNORECASE)
        found_mentions = []
        for p in soup.find_all(['p', 'td', 'li']):
            text = p.get_text().strip()
            if sub_pattern.search(text) and any(kw in text.lower() for kw in ['qib', 'nii', 'retail', 'subscrib']):
                found_mentions.append(text[:150])
        
        if found_mentions:
            for m in found_mentions[:5]:
                print(f"  MENTION: {m}")
        else:
            print("  No x-times subscription mentions found.")
        
        # --- Check 3: Is there a separate subscription page link? ---
        print("\n--- SUBSCRIPTION PAGE LINK SEARCH ---")
        sub_links = []
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            text = a.get_text().lower()
            if 'subscri' in href or 'subscri' in text or 'allotment' in href:
                sub_links.append((a.get_text().strip()[:60], a['href']))
        
        if sub_links:
            for text, link in sub_links[:5]:
                print(f"  LINK: '{text}' → {link}")
        else:
            print("  No subscription-specific links found.")
        
        # --- Check 4: Check if chittorgarh has subscription data ---
        # Try to derive the chittorgarh URL pattern
        slug = url.split('ipowatch.in/')[1].rstrip('/')
        # Chittorgarh URL pattern: /ipo/<name-slug>/XXXX/
        # We can't know the ID without discovery, so check the search
        print("\n--- CHITTORGARH CHECK ---")
        chit_search_url = f"https://www.chittorgarh.com/report/ipo_subscription_status_bse_nse/15/"
        try:
            chit_res = requests.get(chit_search_url, headers=headers, timeout=10)
            if chit_res.status_code == 200:
                chit_soup = BeautifulSoup(chit_res.text, 'html.parser')
                # Look for the IPO name
                name_words = ipo_name.lower().split()[:2]
                found_in_chit = False
                for a in chit_soup.find_all('a', href=True):
                    link_text = a.get_text().lower()
                    if any(w in link_text for w in name_words if len(w) > 3):
                        print(f"  FOUND on chittorgarh: '{a.get_text().strip()[:60]}' → {a['href']}")
                        found_in_chit = True
                        break
                if not found_in_chit:
                    print(f"  Not found on chittorgarh subscription page (may be SME/not listed yet)")
            else:
                print(f"  Chittorgarh returned {chit_res.status_code}")
        except Exception as e:
            print(f"  Chittorgarh error: {e}")
        
        print()
        
    except Exception as e:
        print(f"ERROR for {ipo_name}: {e}")
    
    import time
    time.sleep(1)

print("=" * 70)
print("CONCLUSION: Check above for subscription data availability.")
print("=" * 70)
