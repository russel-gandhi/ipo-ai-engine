import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

def fetch_ipowatch_page(url):
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        if res.status_code == 200:
            return BeautifulSoup(res.content, 'html.parser')
    except:
        pass
    return None

def parse_ipo_page(url, is_sme=False):
    soup = fetch_ipowatch_page(url)
    if not soup:
        return None
        
    try:
        # H1 Company Name
        h1 = soup.find('h1')
        if not h1: return None
        company = h1.text.replace('IPO', '').replace('GMP', '').replace('Details', '').strip()
        
        # Default initialization
        sector = "Unknown"
        issue_size = 0.0
        price_band = 0.0
        sub_retail = 1.0
        sub_qib = 1.0
        sub_nii = 1.0
        sub_overall = 1.0
        listing_date = None
        listing_gain = 0.0
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = [c.text.strip().lower() for c in row.find_all(['th', 'td'])]
                if len(cols) >= 2:
                    key = cols[0]
                    val = cols[1]
                    
                    if 'industry' in key:
                        sector = cols[1].title()
                    elif 'issue size' in key and 'cr' in val:
                        try:
                            # Extract number like 9,273.64
                            num_str = re.sub(r'[^\d.]', '', val.split('cr')[0])
                            issue_size = float(num_str) if num_str else 0.0
                        except: pass
                    elif 'price band' in key and 'to' in val:
                        try:
                            num_str = re.sub(r'[^\d.]', '', val.split('to')[1])
                            price_band = float(num_str) if num_str else 0.0
                        except: pass
                    elif 'listing date' in key:
                        # try to parse date like "April 19, 2023"
                        try:
                            date_str = val.replace(',', '').split('20')[0] + " 20" + val.split('20')[1][:2]
                            listing_date = datetime.strptime(date_str.strip().title(), "%B %d %Y").strftime("%Y-%m-%d")
                        except:
                            pass
        
        if issue_size == 0.0:
            return None
            
        return {
            'company': company,
            'sector': sector,
            'issue_size': issue_size,
            'fresh_vs_ofs_ratio': 1.0, # Defaulting if not found
            'price_band': price_band,
            'sub_retail': sub_retail,
            'sub_nii': sub_nii,
            'sub_qib': sub_qib,
            'sub_overall': sub_overall,
            'gmp_trend': 'flat',
            'actual_listing_gain_pct': listing_gain,
            'source_url': url,
            'listing_gain_bucket': 'flat',
            'data_source': 'real_scraped',
            'is_sme': is_sme,
            'listing_date': listing_date or '2023-01-01', # fallback
            'anchor_allocation_pct': 0.0
        }
    except Exception as e:
        return None

def sync_historical_data():
    print("Starting historical sync...")
    
    # We will scrape the main GMP page which has links to recent IPOs
    soup = fetch_ipowatch_page('https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/')
    if not soup:
        print("Failed to fetch main page")
        return
        
    links = []
    for tr in soup.find_all('tr'):
        a_tag = tr.find('a')
        if a_tag and 'href' in a_tag.attrs:
            url = a_tag['href']
            if 'ipo' in url:
                links.append((url, 'sme' in url.lower()))
                
    print(f"Found {len(links)} IPO URLs. Scraping in parallel...")
    
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for url, is_sme in links[:10]: # LIMITING TO 10 FOR TESTING
            futures.append(executor.submit(parse_ipo_page, url, is_sme))
            
        for future in futures:
            res = future.result()
            if res:
                results.append(res)
                print(f"Success: {res['company']} ({res['listing_date']})")
                
    print(f"Scraped {len(results)} valid IPOs.")

if __name__ == "__main__":
    sync_historical_data()
