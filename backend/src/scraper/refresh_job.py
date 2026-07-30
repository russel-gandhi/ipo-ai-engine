import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'live_ipos.json')

def clean_rupee(val: str) -> float:
    """Removes the rupee symbol and commas, returns a float."""
    try:
        val = val.replace('\u20b9', '').replace(',', '').replace('₹', '').strip()
        if not val or val.lower() == 'na':
            return 0.0
        return float(val)
    except Exception:
        return 0.0

def scrape_ipo_watch():
    """
    Scrapes the IPO GMP page from IPO Watch and saves it to a JSON file.
    Does not crash on failure to ensure API stability.
    """
    url = "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    live_data = []
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        
        if not tables:
            logger.warning("No tables found on IPO Watch GMP page.")
            return

        for row in tables[0].find_all('tr')[1:]: # Skip header
            cols = row.find_all('td')
            if len(cols) >= 6:
                name = cols[0].text.strip()
                gmp_str = cols[1].text.strip()
                trend_raw = cols[2].text.strip().lower()
                price_band_str = cols[3].text.strip()
                
                # Normalize Trend
                trend = "flat"
                if "up" in trend_raw or "rise" in trend_raw:
                    trend = "rising"
                elif "down" in trend_raw or "fall" in trend_raw:
                    trend = "falling"
                
                # Parse Price
                # Usually "₹100 - ₹120", we take the upper band
                price = 0.0
                if '-' in price_band_str:
                    parts = price_band_str.split('-')
                    price = clean_rupee(parts[-1])
                else:
                    price = clean_rupee(price_band_str)
                
                gmp = clean_rupee(gmp_str)
                
                est_listing_gain_pct = round((gmp / price * 100), 2) if price > 0 else 0.0
                
                if name:
                    live_data.append({
                        "name": name,
                        "gmp": gmp,
                        "price_band": price,
                        "gmp_trend": trend,
                        "est_listing_gain_pct": est_listing_gain_pct
                    })
                    
        # Persistence
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        output = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "ipos": live_data
        }
        
        # Atomic write to prevent corruption
        temp_file = DATA_FILE + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4)
        os.replace(temp_file, DATA_FILE)
        
        logger.info(f"Successfully scraped {len(live_data)} live IPOs.")
        
    except requests.RequestException as e:
        logger.error(f"Network error scraping IPO Watch: {e}")
    except Exception as e:
        logger.error(f"Error parsing IPO Watch data: {e}")

if __name__ == "__main__":
    # Test run
    scrape_ipo_watch()
