"""
Check subscription data from chittorgarh IPO detail page.
Chittorgarh.com often has subscription data embedded in the detail page.
Also check investorgain.com and other sources.
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

# Check chittorgarh for a currently open IPO with subscription data
print("=" * 60)
print("CHECK 1: Chittorgarh detail page for recent IPO")
print("=" * 60)

# H.R. Hygiene - should have subscription data as it's closing
urls_to_try = [
    ("Chittorgarh HR Hygiene", "https://www.chittorgarh.com/ipo/hr-hygiene-products-ipo/2037/"),
    ("Chittorgarh Anawil Wire", "https://www.chittorgarh.com/ipo/anawil-wire-and-engineering-ipo/2040/"),
]

for label, url in urls_to_try:
    print(f"\n--- {label} ---")
    print(f"URL: {url}")
    try:
        res = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {res.status_code}")
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")
            
            for ti, table in enumerate(tables):
                table_text = table.get_text().lower()
                # Check for subscription data
                if any(k in table_text for k in ['subscription', 'times', 'subscribed']):
                    rows = table.find_all('tr')
                    print(f"\n  SUBSCRIPTION Table {ti} ({len(rows)} rows):")
                    for ri, row in enumerate(rows):
                        cols = [c.text.strip().replace('\n', ' ')[:80] for c in row.find_all(['th', 'td'])]
                        print(f"    R{ri}: {cols}")
                
                # Also check first few tables for basics
                if ti < 5:
                    rows = table.find_all('tr')
                    has_key_data = any(
                        any(k in c.text.strip().lower() for k in ['lot size', 'price band', 'listing at', 'ipo date', 'issue size'])
                        for row in rows for c in row.find_all(['th', 'td'])
                    )
                    if has_key_data:
                        print(f"\n  KEY DATA Table {ti} ({len(rows)} rows):")
                        for ri, row in enumerate(rows):
                            cols = [c.text.strip().replace('\n', ' ')[:80] for c in row.find_all(['th', 'td'])]
                            print(f"    R{ri}: {cols}")
    except Exception as e:
        print(f"  Error: {e}")

# Check investorgain.com for subscription data
print(f"\n{'=' * 60}")
print("CHECK 2: Investorgain.com subscription status")
print(f"{'=' * 60}")

try:
    inv_url = "https://www.investorgain.com/report/live-ipo-gmp/331/ipo/"
    res_inv = requests.get(inv_url, headers=headers, timeout=15)
    print(f"Status: {res_inv.status_code}")
    
    if res_inv.status_code == 200:
        soup_inv = BeautifulSoup(res_inv.text, 'html.parser')
        tables_inv = soup_inv.find_all('table')
        print(f"Found {len(tables_inv)} tables")
        
        for ti, table in enumerate(tables_inv[:3]):
            rows = table.find_all('tr')
            print(f"\n  Table {ti} ({len(rows)} rows):")
            for ri, row in enumerate(rows[:8]):
                cols = [c.text.strip().replace('\n', ' ')[:60] for c in row.find_all(['th', 'td'])]
                print(f"    R{ri}: {cols}")
except Exception as e:
    print(f"  Error: {e}")

# Check moneycontrol for subscription data  
print(f"\n{'=' * 60}")
print("CHECK 3: Moneycontrol IPO subscription")
print(f"{'=' * 60}")

try:
    mc_url = "https://www.moneycontrol.com/ipo/ipo-live-subscription-status/"
    res_mc = requests.get(mc_url, headers=headers, timeout=15)
    print(f"Status: {res_mc.status_code}")
    
    if res_mc.status_code == 200:
        soup_mc = BeautifulSoup(res_mc.text, 'html.parser')
        tables_mc = soup_mc.find_all('table')
        print(f"Found {len(tables_mc)} tables")
        
        for ti, table in enumerate(tables_mc[:3]):
            rows = table.find_all('tr')
            print(f"\n  Table {ti} ({len(rows)} rows):")
            for ri, row in enumerate(rows[:8]):
                cols = [c.text.strip().replace('\n', ' ')[:60] for c in row.find_all(['th', 'td'])]
                print(f"    R{ri}: {cols}")
except Exception as e:
    print(f"  Error: {e}")
