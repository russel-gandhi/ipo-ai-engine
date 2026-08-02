import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import hashlib
from datetime import datetime, timezone, timedelta
import logging

# ---------------------------------------------------------------------------
# Logging — two handlers: console + scraper_errors.log
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
ERROR_LOG_PATH = os.path.join(DATA_DIR, 'scraper_errors.log')
os.makedirs(DATA_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File handler for structured error tracking (silent failures must be logged)
_fh = logging.FileHandler(ERROR_LOG_PATH, encoding='utf-8')
_fh.setLevel(logging.WARNING)
_fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(_fh)

DATA_FILE = os.path.join(DATA_DIR, 'live_ipos.json')
DETAIL_CACHE_DIR = os.path.join(os.path.dirname(__file__), '.cache', 'details')
os.makedirs(DETAIL_CACHE_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

DETAIL_CACHE_TTL_HOURS = 24


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def clean_rupee(val: str) -> float:
    """Removes the rupee symbol and commas, returns a float."""
    try:
        val = val.replace('\u20b9', '').replace(',', '').replace('₹', '').strip()
        if not val or val.lower() == 'na':
            return 0.0
        return float(val)
    except Exception:
        return 0.0


def clean_rupee_or_none(val: str):
    """Like clean_rupee but returns None instead of 0.0 on failure."""
    try:
        val = val.replace('\u20b9', '').replace(',', '').replace('₹', '').strip()
        if not val or val.lower() in ('na', 'n/a', '-', ''):
            return None
        result = float(val)
        return result if result != 0.0 else None
    except Exception:
        return None


def parse_int_or_none(val: str):
    """Parse an integer from a string, return None on failure."""
    try:
        cleaned = val.replace(',', '').replace(' ', '').strip()
        if not cleaned or cleaned.lower() in ('na', 'n/a', '-'):
            return None
        return int(float(cleaned))
    except Exception:
        return None


def parse_float_or_none(val: str):
    """Parse a float from a string, return None on failure."""
    try:
        cleaned = re.sub(r'[₹,\s]', '', val).strip()
        if not cleaned or cleaned.lower() in ('na', 'n/a', '-', ''):
            return None
        parts = cleaned.split('.')
        if len(parts) > 2:
            cleaned = parts[0] + '.' + parts[1]
        result = float(cleaned)
        return result
    except Exception:
        return None


def parse_percentage(val: str):
    """Parse a percentage like '35%' or '33.30%' into a float."""
    try:
        cleaned = val.replace('%', '').replace(' ', '').strip()
        if not cleaned or cleaned.lower() in ('na', 'n/a', '-'):
            return None
        return float(cleaned)
    except Exception:
        return None


def parse_date(val: str):
    """Try to parse a date string into ISO format YYYY-MM-DD."""
    if not val or not val.strip():
        return None
    val = val.strip()
    val = re.sub(r'\s+', ' ', val).strip().rstrip(',')

    formats = [
        "%B %d, %Y",
        "%B %d %Y",
        "%b %d, %Y",
        "%b %d %Y",
        "%d %B, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(val, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    try:
        cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', val)
        for fmt in formats:
            try:
                return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    except Exception:
        pass

    return None


def url_to_cache_key(url: str) -> str:
    """Generate a filesystem-safe cache key from a URL."""
    return hashlib.md5(url.encode()).hexdigest() + '.html'


def get_cached_html(url: str):
    """Return cached HTML if fresh, else None."""
    cache_path = os.path.join(DETAIL_CACHE_DIR, url_to_cache_key(url))
    if os.path.exists(cache_path):
        mtime = datetime.fromtimestamp(os.path.getmtime(cache_path), tz=timezone.utc)
        if datetime.now(timezone.utc) - mtime < timedelta(hours=DETAIL_CACHE_TTL_HOURS):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()
    return None


def cache_html(url: str, html: str):
    """Cache HTML to disk."""
    cache_path = os.path.join(DETAIL_CACHE_DIR, url_to_cache_key(url))
    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write(html)


def normalize_trend(raw: str) -> str:
    """Normalize GMP trend emoji/text to rising/falling/flat."""
    raw = raw.lower().strip()
    if '🟢' in raw or 'up' in raw or 'rise' in raw or 'rising' in raw:
        return 'rising'
    if '🔴' in raw or 'down' in raw or 'fall' in raw or 'falling' in raw:
        return 'falling'
    return 'flat'


def normalize_status(raw: str, close_date_str: str = None) -> str:
    """Normalize status to open/closing_today/upcoming/closed."""
    raw = raw.lower().strip()
    if 'upcoming' in raw:
        return 'upcoming'
    if 'closed' in raw or 'listed' in raw:
        return 'closed'
    if 'open' in raw or 'subscribe' in raw:
        if close_date_str:
            try:
                close_date = datetime.strptime(close_date_str, "%Y-%m-%d").date()
                today = datetime.now().date()
                if close_date == today:
                    return 'closing_today'
            except Exception:
                pass
        return 'open'
    return 'upcoming'


def parse_exchange_type(type_col: str):
    """Parse the Type column from GMP table into exchange and is_sme."""
    raw = type_col.strip()
    is_sme = 'sme' in raw.lower()
    if 'bse sme' in raw.lower():
        exchange = 'BSE SME'
    elif 'nse sme' in raw.lower():
        exchange = 'NSE SME'
    elif 'mainboard' in raw.lower():
        exchange = 'NSE, BSE'
    else:
        exchange = raw if raw else None
    return exchange, is_sme


def parse_date_range_from_gmp(date_col: str, year: int = None):
    """
    Parse the Date column from GMP table (e.g. '31-4 August', '29-31 July')
    into (open_date, close_date) as ISO strings.
    """
    if not date_col or not date_col.strip():
        return None, None

    if year is None:
        year = datetime.now().year

    raw = date_col.strip()
    match = re.match(r'(\d+)-(\d+)\s+(\w+)', raw)
    if match:
        day1, day2, month = int(match.group(1)), int(match.group(2)), match.group(3)
        try:
            if day1 > day2:
                close_date = datetime.strptime(f"{day2} {month} {year}", "%d %B %Y")
                if close_date.month == 1:
                    open_date = close_date.replace(year=year - 1, month=12, day=day1)
                else:
                    open_date = close_date.replace(month=close_date.month - 1, day=day1)
            else:
                open_date = datetime.strptime(f"{day1} {month} {year}", "%d %B %Y")
                close_date = datetime.strptime(f"{day2} {month} {year}", "%d %B %Y")
            return open_date.strftime("%Y-%m-%d"), close_date.strftime("%Y-%m-%d")
        except Exception:
            pass

    return None, None


# ---------------------------------------------------------------------------
# Table helpers
# ---------------------------------------------------------------------------

def _find_table_by_header(tables, header_keywords):
    """Find a table whose first row contains any of the given keywords."""
    for table in tables:
        rows = table.find_all('tr')
        if not rows:
            continue
        first_row_text = rows[0].get_text().lower()
        if any(kw in first_row_text for kw in header_keywords):
            return table
    return None


def _find_kv_table(tables, key_keyword):
    """Find a key-value table that has a row with the given keyword."""
    for table in tables:
        for row in table.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 2:
                if key_keyword.lower() in cells[0].get_text().lower():
                    return table
    return None


def _get_kv_from_table(table, key_keyword):
    """
    Get the value cell text for a given key in a key-value table.
    Returns None if table is None or key not found.
    """
    if not table:
        return None
    for row in table.find_all('tr'):
        cells = row.find_all(['th', 'td'])
        if len(cells) >= 2:
            if key_keyword.lower() in cells[0].get_text().lower():
                return cells[1].get_text(separator=' ').strip()
    return None


# ---------------------------------------------------------------------------
# Sector extraction helpers
# ---------------------------------------------------------------------------

# Curated sector keyword map — applied to the about text.
# Explicit categories > regex extraction (avoids "Research Driven" etc.)
# Curated sector keyword map — ordered list, most specific first.
# Earlier entries take priority over later ones.
# "technology" is intentionally last — it's too generic and appears in many
# non-tech about texts (e.g. "Research Driven Technology").
SECTOR_KEYWORDS = [
    ('Education',           ['edtech', 'education technology', 'e-learning', 'digital learning',
                             'education', 'school', 'training platform', 'learning platform', 'skill development']),
    ('Healthcare',          ['pharma', 'pharmaceutical', 'hospital', 'healthcare', 'medical device',
                             'biotech', 'diagnostic', 'drug', 'clinic', 'health tech']),
    ('Financial Services',  ['nbfc', 'insurance', 'lending', 'microfinance', 'banking',
                             'asset management', 'wealth management', 'financial service', 'fintech']),
    ('Energy',              ['solar', 'wind energy', 'renewable energy', 'power generation',
                             'green energy', 'electric vehicle', 'ev charging']),
    ('Consumer',            ['retail chain', 'e-commerce', 'fashion', 'food and beverage',
                             'consumer goods', 'fmcg', 'hygiene products', 'personal care', 'beauty']),
    ('Manufacturing',       ['manufacturing', 'industrial', 'engineering company', 'auto component',
                             'automobile parts', 'packaging', 'textile', 'chemical', 'steel', 'wire manufacturer',
                             'electrical component']),
    ('Infrastructure',      ['infrastructure', 'construction', 'real estate', 'logistics',
                             'transport', 'warehouse', 'road construction']),
    ('Agriculture',         ['agri', 'farming', 'food processing', 'seed', 'fertilizer']),
    # Technology is last — broad term, only match when more specific terms don't
    ('Technology',          ['software company', 'saas', 'it services', 'cloud computing',
                             'cybersecurity', 'artificial intelligence', 'data analytics',
                             'information technology company']),
]


def extract_sector_from_text(text: str) -> str:
    """
    Match about text against curated sector keyword list (ordered by specificity).
    Returns the sector label or None.
    Never returns a wrong value — null is preferred over a misidentification.
    """
    if not text:
        return None
    text_lower = text.lower()
    for sector, keywords in SECTOR_KEYWORDS:
        if any(kw in text_lower for kw in keywords):
            return sector
    return None


# ---------------------------------------------------------------------------
# Pass 1: Enhanced GMP Table Scrape
# ---------------------------------------------------------------------------

def scrape_gmp_table():
    """
    Scrapes the ipowatch.in GMP table and extracts enhanced fields per IPO.
    Returns a list of dicts with GMP-level fields + detail_url.
    """
    url = "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/"
    ipos = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')

        if not tables:
            logger.warning("No tables found on IPO Watch GMP page.")
            return ipos

        for row in tables[0].find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) < 8:
                continue

            name = cols[0].text.strip()
            if not name:
                continue

            a_tag = cols[0].find('a')
            detail_url = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None

            gmp = clean_rupee(cols[1].text.strip())
            gmp_trend = normalize_trend(cols[2].text.strip())

            price_band_str = cols[3].text.strip()
            price = 0.0
            if '-' in price_band_str:
                parts = price_band_str.split('-')
                price = clean_rupee(parts[-1])
            else:
                price = clean_rupee(price_band_str)

            est_listing_gain_pct = round((gmp / price * 100), 2) if price > 0 else 0.0

            date_col = cols[5].text.strip() if len(cols) > 5 else ''
            open_date_gmp, close_date_gmp = parse_date_range_from_gmp(date_col)

            type_col = cols[6].text.strip() if len(cols) > 6 else ''
            exchange, is_sme = parse_exchange_type(type_col)

            status_raw = cols[7].text.strip() if len(cols) > 7 else ''
            status = normalize_status(status_raw, close_date_gmp)

            ipos.append({
                "name": name,
                "gmp": gmp,
                "price_band": price,
                "gmp_trend": gmp_trend,
                "est_listing_gain_pct": est_listing_gain_pct,
                "detail_url": detail_url,
                "exchange": exchange,
                "is_sme": is_sme,
                "status": status,
                "open_date": open_date_gmp,
                "close_date": close_date_gmp,
            })

        logger.info(f"Pass 1: Scraped {len(ipos)} IPOs from GMP table.")

    except requests.RequestException as e:
        logger.error(f"Network error scraping GMP table: {e}")
    except Exception as e:
        logger.error(f"Error parsing GMP table: {e}")

    return ipos


# ---------------------------------------------------------------------------
# Pass 2: Detail Page Scraping
# ---------------------------------------------------------------------------

def fetch_detail_html(detail_url: str) -> str:
    """Fetch detail page HTML with caching."""
    cached = get_cached_html(detail_url)
    if cached:
        return cached

    try:
        response = requests.get(detail_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html = response.text
        cache_html(detail_url, html)
        time.sleep(0.5)
        return html
    except Exception as e:
        logger.error(f"Error fetching detail page {detail_url}: {e}")
        return None


def _scope_to_ipo_section(soup, ipo_name: str):
    """
    ipowatch.in detail pages contain content for MULTIPLE IPOs.
    The structure is:
      [h1] Some Other IPO review      ← sidebar/earlier IPO, NOT ours
      [tables for that IPO...]
      [h1] OUR IPO Date, Review...    ← this is the target section start
      [tables for our IPO...]

    Strategy: find the H1 that matches our IPO name. Everything AFTER it
    (until the next unrelated H1 or end of page) is in scope.

    Returns (scoped_tables, scoped_paragraphs, success: bool).
    If scoping fails, returns ([], [], False) — callers must log and use nulls.
    """
    ipo_name_lower = ipo_name.lower().strip()
    # Strip common suffixes that may not appear in headings
    ipo_name_clean = re.sub(
        r'\s+(ipo|ltd\.?|limited|pvt\.?|private|industries|products|technologies|systems)$',
        '', ipo_name_lower, flags=re.IGNORECASE
    ).strip()

    # Find the target H1
    target_h1 = None
    all_h1 = soup.find_all('h1')
    for h1 in all_h1:
        h1_text = h1.get_text().lower().strip()
        # Match: all significant words from our IPO name appear in the heading
        name_words = [w for w in ipo_name_clean.split() if len(w) > 2]
        if name_words and all(w in h1_text for w in name_words):
            target_h1 = h1
            break
        # Fallback: any reasonable substring match
        if ipo_name_clean and len(ipo_name_clean) > 4 and ipo_name_clean in h1_text:
            target_h1 = h1
            break

    if not target_h1:
        # Try partial match — at least 60% of words match
        for h1 in all_h1:
            h1_text = h1.get_text().lower().strip()
            name_words = [w for w in ipo_name_clean.split() if len(w) > 2]
            if name_words:
                match_count = sum(1 for w in name_words if w in h1_text)
                if match_count / len(name_words) >= 0.6:
                    target_h1 = h1
                    break

    if not target_h1:
        return [], [], False

    # Collect all elements AFTER the target H1
    scoped_tables = []
    scoped_paragraphs = []
    collecting = False

    for elem in soup.find_all(['h1', 'h2', 'h3', 'table', 'p']):
        if elem is target_h1:
            collecting = True
            continue
        if not collecting:
            continue
        # Stop if we hit another H1 that's about a different IPO
        if elem.name == 'h1':
            h1_text = elem.get_text().lower()
            name_words = [w for w in ipo_name_clean.split() if len(w) > 2]
            if name_words and not any(w in h1_text for w in name_words):
                break  # Left our section
        if elem.name == 'table':
            scoped_tables.append(elem)
        elif elem.name == 'p':
            scoped_paragraphs.append(elem)

    return scoped_tables, scoped_paragraphs, True


def parse_detail_page(html: str, ipo_name: str = "") -> dict:
    """
    Parse an ipowatch.in detail page and extract all available rich fields.

    KEY FIX: ipowatch.in pages contain content for multiple IPOs (sidebar
    reviews appear BEFORE the target IPO's own section). We scope ALL parsing
    to the section that starts with the H1 matching the target IPO name.

    If scoping fails, we return null fields and log a warning. We never fall
    back to using all-page data, which would return another IPO's content.

    Returns a dict with keys matching the output schema. Missing fields are None.
    """
    result = {
        "sector": None,
        "issue_size": None,
        "price_band_range": None,
        "lot_size": None,
        "open_date": None,
        "close_date": None,
        "allotment_date": None,
        "listing_date": None,
        "sub_qib": None,
        "sub_nii": None,
        "sub_retail": None,
        "sub_overall": None,
        "lot_distribution": None,
        "offer_breakdown": None,
        "about": None,
        "issue_objective": None,
        "financials": None,
    }

    if not html:
        return result

    try:
        soup = BeautifulSoup(html, 'html.parser')

        # --- Scope to the correct IPO section ---
        scoped_tables, scoped_paragraphs, scoping_success = _scope_to_ipo_section(soup, ipo_name)

        if not scoping_success or not scoped_tables:
            # IMPORTANT: do NOT fall back to all-page data.
            # Log the failure so it's visible and return null fields.
            logger.warning(
                f"[SCRAPER WARNING] Could not scope tables for '{ipo_name}' — "
                f"returning null fields rather than fallback data. "
                f"Check page structure at the detail URL."
            )
            return result

        tables = scoped_tables

        # --- IPO Details / Dates Table (key-value pairs) ---
        # There are two KV tables: one with IPO dates, one with further details.
        # Try multiple keys to find the right table.
        details_table = (
            _find_kv_table(tables, 'ipo open date')
            or _find_kv_table(tables, 'open date')
            or _find_kv_table(tables, 'ipo price band')
            or _find_kv_table(tables, 'issue size')
        )

        if details_table:
            # Issue Size
            issue_size_raw = _get_kv_from_table(details_table, 'issue size')
            if issue_size_raw:
                cr_match = re.search(r'([\d,.]+)\s*(?:crore|cr)', issue_size_raw, re.IGNORECASE)
                if cr_match:
                    result["issue_size"] = parse_float_or_none(cr_match.group(1))

            # Price Band Range
            price_raw = _get_kv_from_table(details_table, 'price band')
            if price_raw:
                result["price_band_range"] = price_raw.strip()

            # Dates (may be in the same table or a separate dates table)
            open_raw = _get_kv_from_table(details_table, 'open date')
            close_raw = _get_kv_from_table(details_table, 'close date')
            allotment_raw = (
                _get_kv_from_table(details_table, 'basis of allotment')
                or _get_kv_from_table(details_table, 'allotment')
            )
            listing_raw = _get_kv_from_table(details_table, 'listing date')

            if open_raw:
                result["open_date"] = parse_date(open_raw)
            if close_raw:
                result["close_date"] = parse_date(close_raw)
            if allotment_raw:
                result["allotment_date"] = parse_date(allotment_raw)
            if listing_raw:
                result["listing_date"] = parse_date(listing_raw)

        # --- Lot Size / Lot Distribution Table ---
        # Header: Application | Lot Size | Shares | Amount
        lot_table = _find_table_by_header(tables, ['application'])
        if lot_table:
            lot_rows = lot_table.find_all('tr')
            lot_dist = []

            for row in lot_rows[1:]:
                cells = [c.get_text().strip() for c in row.find_all(['th', 'td'])]
                if len(cells) >= 4:
                    app_type = cells[0].lower()
                    # Columns: Application | Lot Size | Shares | Amount
                    lots = parse_int_or_none(cells[1])
                    shares = parse_int_or_none(cells[2])
                    amount = parse_float_or_none(cells[3])

                    if 'retail min' in app_type or ('retail' in app_type and 'min' in app_type):
                        if shares and result["lot_size"] is None:
                            result["lot_size"] = shares
                        lot_dist.append({
                            "category": "Individual",
                            "min_shares": shares,
                            "min_amount": int(amount) if amount else None,
                            "total_lots": lots
                        })
                    elif 's-hni min' in app_type or 'shni min' in app_type or ('s-hni' in app_type):
                        lot_dist.append({
                            "category": "sHNI",
                            "min_shares": shares,
                            "min_amount": int(amount) if amount else None,
                            "total_lots": lots
                        })
                    elif 'b-hni min' in app_type or 'bhni min' in app_type or ('b-hni' in app_type):
                        lot_dist.append({
                            "category": "bHNI",
                            "min_shares": shares,
                            "min_amount": int(amount) if amount else None,
                            "total_lots": lots
                        })

            if lot_dist:
                result["lot_distribution"] = lot_dist

        # --- Offer Breakdown Table ---
        # Header: Investor Category | Share Offered | -% Shares
        offer_table = _find_table_by_header(tables, ['investor category'])
        if offer_table:
            offer = {}
            for row in offer_table.find_all('tr')[1:]:
                cells = [c.get_text().strip() for c in row.find_all(['th', 'td'])]
                if len(cells) >= 2:
                    category = cells[0].lower()
                    # Skip anchor investor rows — they're a subset of QIB, not separate
                    if 'anchor' in category and 'qib' not in category:
                        continue
                    pct = None
                    for cell_text in reversed(cells[1:]):
                        pct = parse_percentage(cell_text)
                        if pct is not None:
                            break

                    if pct is not None:
                        if 'qib' in category:
                            offer['qib_pct'] = pct
                        elif 'nii' in category or 'hni' in category:
                            offer['nii_pct'] = pct
                        elif 'retail' in category:
                            offer['retail_pct'] = pct

            if offer:
                result["offer_breakdown"] = offer

        # --- Issue Objectives Table ---
        # Header: Purpose | Crores
        obj_table = (
            _find_table_by_header(tables, ['purpose'])
            or _find_table_by_header(tables, ['objects of the issue'])
        )
        if obj_table:
            objectives = []
            for row in obj_table.find_all('tr')[1:]:
                cells = [c.get_text().strip() for c in row.find_all(['th', 'td'])]
                if cells and cells[0]:
                    purpose_text = cells[0].strip()
                    if (len(purpose_text) > 10
                            and purpose_text.lower() not in ('purposes', 'total', 'general corporate purposes')):
                        objectives.append(purpose_text)
            if objectives:
                result["issue_objective"] = objectives

        # --- Financials Table ---
        # Header: Period Ended | Revenue | Expense | PAT | Assets
        fin_table = (
            _find_table_by_header(tables, ['period ended'])
            or _find_table_by_header(tables, ['period', 'revenue'])
        )
        if fin_table:
            financials = []
            for row in fin_table.find_all('tr')[1:]:
                cells = [c.get_text().strip() for c in row.find_all(['th', 'td'])]
                if len(cells) >= 4:
                    period = cells[0].strip()
                    revenue = parse_float_or_none(cells[1])
                    # PAT is typically column 3 (index 3) if 5 columns,
                    # or column 2 if 4 columns
                    profit = parse_float_or_none(cells[3]) if len(cells) >= 5 else parse_float_or_none(cells[2])
                    assets = parse_float_or_none(cells[4]) if len(cells) >= 5 else parse_float_or_none(cells[3])

                    if period and (revenue is not None or profit is not None):
                        financials.append({
                            "period": period,
                            "revenue": revenue,
                            "profit": profit,
                            "assets": assets,
                        })
            if financials:
                result["financials"] = financials

        # --- About / Company Description ---
        # Use scoped paragraphs only. Find the first paragraph that is a genuine
        # company description (not boilerplate).
        boilerplate_keywords = [
            'disclaimer', 'dilip davda', 'merchant banker',
            'email address', 'save my name', 'official platform',
            'comment', 'not published', 'filed drhp',
            'gmp is', 'grey market premium', 'ipowatch'
        ]

        for p in scoped_paragraphs:
            text = p.get_text().strip()
            if len(text) > 80:
                text_lower = text.lower()
                if not any(kw in text_lower for kw in boilerplate_keywords):
                    result["about"] = text
                    break

        # --- Sector --- (derived from about text using curated keyword map)
        if result["about"]:
            result["sector"] = extract_sector_from_text(result["about"])

        # NOTE ON SUBSCRIPTION DATA:
        # ipowatch.in detail pages do NOT contain subscription multiples
        # (sub_qib, sub_nii, sub_retail, sub_overall). These figures only appear
        # on separate subscription status pages, and only after the issue opens.
        # sub_* fields will remain null for upcoming/open IPOs. This is honest.
        # The frontend handles this gracefully with "Subscription data not yet
        # available — check back after the issue opens."

    except Exception as e:
        logger.error(f"Error parsing detail page for '{ipo_name}': {e}")

    return result


# ---------------------------------------------------------------------------
# Main scraper orchestration
# ---------------------------------------------------------------------------

def scrape_ipo_watch():
    """
    Two-pass scraper:
    Pass 1: GMP table for overview data + detail URLs
    Pass 2: Detail pages for rich per-IPO fields
    Merges both passes and writes to live_ipos.json.
    Does not crash on failure to ensure API stability.
    """

    # Pass 1: GMP table
    ipos = scrape_gmp_table()
    if not ipos:
        logger.warning("Pass 1 returned no IPOs. Skipping Pass 2.")
        return

    # Pass 2: Detail pages — only for IPOs with a detail_url
    scoping_failures = []
    for ipo in ipos:
        detail_url = ipo.get("detail_url")
        if not detail_url:
            continue

        try:
            html = fetch_detail_html(detail_url)
            if html:
                # CRITICAL FIX: pass ipo_name so the parser can scope correctly
                detail = parse_detail_page(html, ipo_name=ipo['name'])

                # Check if we got any real data (scoping may have failed silently)
                has_data = any(
                    detail.get(k) is not None
                    for k in ['lot_size', 'about', 'financials', 'issue_objective']
                )
                if not has_data:
                    scoping_failures.append(ipo['name'])

                # Merge detail fields into the IPO object
                # Only overwrite if detail has a non-None value
                for key in detail:
                    if detail[key] is not None:
                        ipo[key] = detail[key]
                    elif key not in ipo:
                        ipo[key] = None

                # Re-check status with precise close_date from detail
                if ipo.get("close_date") and ipo.get("status") == "open":
                    ipo["status"] = normalize_status("open", ipo["close_date"])

                logger.info(
                    f"  Pass 2: Enriched '{ipo['name']}' — "
                    f"lot_size={ipo.get('lot_size')}, "
                    f"sector={ipo.get('sector')}, "
                    f"financials={'yes' if ipo.get('financials') else 'no'}, "
                    f"about={'yes' if ipo.get('about') else 'no'}"
                )
        except Exception as e:
            logger.error(f"  Pass 2: Error enriching '{ipo['name']}': {e}")

    if scoping_failures:
        logger.warning(
            f"[SCRAPER WARNING] Scoping produced no data for {len(scoping_failures)} IPO(s): "
            f"{scoping_failures}. These will have null detail fields. "
            f"Check scraper_errors.log for per-IPO detail."
        )

    # Pass 3: Subscription Status Data
    try:
        sub_url = "https://ipowatch.in/ipo-subscription-status-today/"
        sub_response = requests.get(sub_url, headers=HEADERS, timeout=15)
        sub_response.raise_for_status()
        sub_soup = BeautifulSoup(sub_response.text, 'html.parser')
        
        sub_data = {}
        tables = sub_soup.find_all('table')
        if not tables:
            for fig in sub_soup.find_all('figure', class_='wp-block-table'):
                if fig.find('table'):
                    tables.append(fig.find('table'))
                    
        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue
            header = [th.get_text().strip().lower() for th in rows[0].find_all(['th', 'td'])]
            if 'qib' in str(header):
                for row in rows[1:]:
                    cols = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                    if len(cols) >= 7:
                        name = cols[0]
                        qib = parse_float_or_none(cols[3])
                        nii = parse_float_or_none(cols[4])
                        retail = parse_float_or_none(cols[5])
                        total = parse_float_or_none(cols[6])
                        sub_data[name.lower()] = {
                            "sub_qib": qib,
                            "sub_nii": nii,
                            "sub_retail": retail,
                            "sub_overall": total
                        }
                        
        if sub_data:
            logger.info(f"Pass 3: Scraped subscription data for {len(sub_data)} IPOs.")
            for ipo in ipos:
                name_clean = ipo['name'].lower().strip()
                matched_sub = sub_data.get(name_clean)
                if not matched_sub:
                    for s_name, s_data in sub_data.items():
                        if s_name in name_clean or name_clean in s_name:
                            matched_sub = s_data
                            break
                            
                if matched_sub:
                    ipo["sub_qib"] = matched_sub["sub_qib"]
                    ipo["sub_nii"] = matched_sub["sub_nii"]
                    ipo["sub_retail"] = matched_sub["sub_retail"]
                    ipo["sub_overall"] = matched_sub["sub_overall"]
                    
    except Exception as e:
        logger.error(f"Error scraping subscription status: {e}")

    # Ensure all IPOs have all expected fields (set missing to None)
    all_fields = [
        "name", "gmp", "price_band", "gmp_trend", "est_listing_gain_pct",
        "detail_url", "exchange", "is_sme", "status",
        "sector", "issue_size", "price_band_range", "lot_size",
        "open_date", "close_date", "allotment_date", "listing_date",
        "sub_qib", "sub_nii", "sub_retail", "sub_overall",
        "lot_distribution", "offer_breakdown",
        "about", "issue_objective", "financials",
    ]
    for ipo in ipos:
        for field in all_fields:
            if field not in ipo:
                ipo[field] = None

    # Persistence — atomic write with existing demo metadata preservation
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    # Read existing file to preserve historical demo records (e.g. Zaggle) and enriched fields
    existing_ipos = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_ipos = existing_data.get("ipos", [])
        except Exception:
            existing_ipos = []

    existing_by_name = {item["name"].lower(): item for item in existing_ipos}

    # Merge scraped items with existing items
    final_ipos = []
    scraped_names_lower = set()

    for ipo in ipos:
        name_key = ipo["name"].lower()
        scraped_names_lower.add(name_key)
        existing = existing_by_name.get(name_key)
        if existing:
            # Preserve existing enriched fields if missing in scraped item
            for k, v in existing.items():
                if ipo.get(k) is None and v is not None:
                    ipo[k] = v
        if not ipo.get("slug"):
            ipo["slug"] = re.sub(r'[^a-z0-9]+', '-', ipo["name"].lower()).strip('-')
        final_ipos.append(ipo)

    # Retain historical/demo IPOs (like Zaggle or items with basis_of_allotment) not in live scrape
    for item in existing_ipos:
        name_key = item.get("name", "").lower()
        if name_key not in scraped_names_lower:
            final_ipos.append(item)

    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "ipos": final_ipos
    }

    temp_file = DATA_FILE + ".tmp"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    os.replace(temp_file, DATA_FILE)

    logger.info(f"Successfully scraped and enriched {len(ipos)} live IPOs.")
    if scoping_failures:
        logger.warning(
            f"Scoping failures ({len(scoping_failures)} IPOs) logged to {ERROR_LOG_PATH}"
        )


if __name__ == "__main__":
    import sys
    import shutil

    args = sys.argv[1:]

    if "--clear-cache" in args:
        # Explicit opt-in only — never auto-clear on normal runs
        if os.path.exists(DETAIL_CACHE_DIR):
            shutil.rmtree(DETAIL_CACHE_DIR)
            os.makedirs(DETAIL_CACHE_DIR, exist_ok=True)
            print(f"Cache cleared: {DETAIL_CACHE_DIR}")

    if "--reparse" in args:
        # Re-parse any HTML files already in cache using the fixed parser.
        # Does NOT make any network requests. Useful when ipowatch.in is
        # unreachable but cached HTML exists from a previous run.
        print("--reparse mode: using cached HTML only, no network requests.")
        cached_files = [f for f in os.listdir(DETAIL_CACHE_DIR) if f.endswith('.html')]
        print(f"Found {len(cached_files)} cached HTML files to reparse.")

        # Load existing live_ipos.json to get the name→URL mapping
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            ipos = existing.get('ipos', [])
        else:
            print("No live_ipos.json found. Run without --reparse first.")
            sys.exit(1)

        for ipo in ipos:
            detail_url = ipo.get('detail_url')
            if not detail_url:
                continue
            cache_path = os.path.join(DETAIL_CACHE_DIR, url_to_cache_key(detail_url))
            if not os.path.exists(cache_path):
                logger.warning(
                    f"[SCRAPER WARNING] Could not scope tables for '{ipo['name']}' — "
                    f"returning null fields rather than fallback data. "
                    f"No cached HTML found — run without --reparse to fetch from network."
                )
                continue
            with open(cache_path, 'r', encoding='utf-8') as f:
                html = f.read()
            detail = parse_detail_page(html, ipo_name=ipo['name'])
            for key in detail:
                if detail[key] is not None:
                    ipo[key] = detail[key]

            logger.info(
                f"Reparsed '{ipo['name']}' — "
                f"lot_size={ipo.get('lot_size')}, sector={ipo.get('sector')}, "
                f"about={'yes' if ipo.get('about') else 'no'}"
            )

        # Write updated data
        output = {
            "last_updated": existing.get('last_updated', datetime.now(timezone.utc).isoformat()),
            "ipos": ipos
        }
        temp_file = DATA_FILE + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, DATA_FILE)
        print(f"Reparsed {len(ipos)} IPOs and wrote to live_ipos.json.")

    else:
        # Normal mode: full two-pass scrape with network requests
        scrape_ipo_watch()
