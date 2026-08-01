"""
Unit tests for the fixed refresh_job.py scraper.
Tests the _scope_to_ipo_section and parse_detail_page functions
using hardcoded HTML that mimics the real ipowatch.in page structure.

Run: python scratch/test_scraper_fix.py
"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.scraper.refresh_job import (
    _scope_to_ipo_section,
    parse_detail_page,
    extract_sector_from_text,
    _get_kv_from_table,
    _find_kv_table,
)
from bs4 import BeautifulSoup

PASS = 0
FAIL = 0

def check(name, actual, expected):
    global PASS, FAIL
    if actual == expected:
        print(f"  [PASS] {name}")
        PASS += 1
    else:
        print(f"  [FAIL] {name}")
        print(f"      expected: {repr(expected)}")
        print(f"      actual:   {repr(actual)}")
        FAIL += 1

# ---------------------------------------------------------------------------
# Test 1: _get_kv_from_table — was completely broken (no function body)
# ---------------------------------------------------------------------------
print("\n=== Test 1: _get_kv_from_table ===")

kv_html = """
<table>
  <tr><td>IPO Open Date</td><td>July 31, 2026</td></tr>
  <tr><td>IPO Close Date</td><td>August 2, 2026</td></tr>
  <tr><td>Issue Size</td><td>500 Crore</td></tr>
  <tr><td>Price Band</td><td>₹83-₹88</td></tr>
</table>
"""
soup = BeautifulSoup(kv_html, 'html.parser')
tables = soup.find_all('table')

check("open date lookup", _get_kv_from_table(tables[0], 'open date'), "July 31, 2026")
check("close date lookup", _get_kv_from_table(tables[0], 'close date'), "August 2, 2026")
check("issue size lookup", _get_kv_from_table(tables[0], 'issue size'), "500 Crore")
check("None table returns None", _get_kv_from_table(None, 'open date'), None)
check("missing key returns None", _get_kv_from_table(tables[0], 'listing date'), None)

# ---------------------------------------------------------------------------
# Test 2: _scope_to_ipo_section — the core bug fix
# ---------------------------------------------------------------------------
print("\n=== Test 2: _scope_to_ipo_section ===")

# Mimics the EXACT ipowatch.in structure:
# - First h1 is a sidebar review for Q-Line Biotech (WRONG IPO)
# - Second h1 is the actual target IPO's section
IPOWATCH_LIKE_HTML = """
<html><body>
  <!-- SIDEBAR / earlier IPO review — should be OUT of scope -->
  <h1>Q-Line Biotech NSE SME IPO review</h1>
  <p>Q-Line Biotech Ltd. (QBL) is engaged in the business of developing, manufacturing...</p>
  <table>
    <tr><th>Period Ended</th><th>Revenue</th><th>Expense</th><th>PAT</th><th>Assets</th></tr>
    <tr><td>2023</td><td>184.81</td><td>150.0</td><td>32.1</td><td>251.58</td></tr>
  </table>

  <!-- TARGET IPO section — ONLY these should be in scope -->
  <h1>Fusion Klassroom IPO Date, Review, Price, Allotment Details</h1>
  <p>Fusion Klassroom is a leading EdTech company offering digital learning solutions...</p>
  <table>
    <tr><td>IPO Open Date</td><td>July 31, 2026</td></tr>
    <tr><td>IPO Close Date</td><td>August 2, 2026</td></tr>
    <tr><td>Issue Size</td><td>39 Crore</td></tr>
  </table>
  <table>
    <tr><th>Application</th><th>Lot Size</th><th>Shares</th><th>Amount</th></tr>
    <tr><td>Retail Min</td><td>1</td><td>1600</td><td>48000</td></tr>
  </table>
  <table>
    <tr><th>Investor Category</th><th>Share Offered</th><th>-% Shares</th></tr>
    <tr><td>QIB</td><td>1000000</td><td>50%</td></tr>
    <tr><td>NII/HNI</td><td>300000</td><td>15%</td></tr>
    <tr><td>Retail</td><td>660000</td><td>33%</td></tr>
  </table>
  <table>
    <tr><th>Period Ended</th><th>Revenue</th><th>Expense</th><th>PAT</th><th>Assets</th></tr>
    <tr><td>FY2024</td><td>25.5</td><td>18.0</td><td>5.2</td><td>42.1</td></tr>
    <tr><td>FY2023</td><td>18.3</td><td>14.0</td><td>3.1</td><td>35.0</td></tr>
  </table>
  <table>
    <tr><th>Purpose</th><th>Crores</th></tr>
    <tr><td>Technology infrastructure expansion</td><td>20</td></tr>
    <tr><td>Working capital</td><td>12</td></tr>
  </table>
</body></html>
"""

soup2 = BeautifulSoup(IPOWATCH_LIKE_HTML, 'html.parser')
tables2, paragraphs2, success = _scope_to_ipo_section(soup2, "Fusion Klassroom")

check("scoping succeeds", success, True)
check("scoped tables count (should be 5: dates/lot/offer/financials/obj)", len(tables2), 5)
check("scoped paragraphs count (should be 1)", len(paragraphs2), 1)

# The scoped paragraph should be about Fusion Klassroom, NOT Q-Line Biotech
if paragraphs2:
    p_text = paragraphs2[0].get_text()
    check("about text is Fusion Klassroom, not Q-Line Biotech", 
          "Q-Line Biotech" not in p_text, True)
    check("about text contains correct IPO", "Fusion Klassroom" in p_text, True)

# ---------------------------------------------------------------------------
# Test 3: parse_detail_page end-to-end with the fixed HTML
# ---------------------------------------------------------------------------
print("\n=== Test 3: parse_detail_page end-to-end ===")

result = parse_detail_page(IPOWATCH_LIKE_HTML, ipo_name="Fusion Klassroom")

check("open_date parsed", result['open_date'], "2026-07-31")
check("close_date parsed", result['close_date'], "2026-08-02")
check("issue_size parsed", result['issue_size'], 39.0)
check("lot_size from lot table", result['lot_size'], 1600)
check("lot_distribution populated", result['lot_distribution'] is not None, True)
check("lot_distribution has Individual entry", 
      result['lot_distribution'][0]['category'] if result['lot_distribution'] else None,
      "Individual")
check("offer_breakdown qib_pct", result['offer_breakdown'].get('qib_pct') if result['offer_breakdown'] else None, 50.0)
check("offer_breakdown nii_pct", result['offer_breakdown'].get('nii_pct') if result['offer_breakdown'] else None, 15.0)
check("offer_breakdown retail_pct", result['offer_breakdown'].get('retail_pct') if result['offer_breakdown'] else None, 33.0)
check("financials populated", result['financials'] is not None, True)
check("financials count (2 rows)", len(result['financials']) if result['financials'] else 0, 2)
check("financials first period", result['financials'][0]['period'] if result['financials'] else None, "FY2024")
check("issue_objective populated", result['issue_objective'] is not None, True)
check("about is NOT Q-Line Biotech", 
      "Q-Line Biotech" not in (result['about'] or ''), True)
check("about is Fusion Klassroom", 
      "Fusion Klassroom" in (result['about'] or ''), True)
check("sector = Education (from EdTech keyword)", result['sector'], "Education")

# Test: when scoping fails, return nulls not wrong data
print("\n=== Test 4: Failed scoping returns nulls, not wrong data ===")

NO_MATCH_HTML = """<html><body>
  <h1>Some Random IPO review</h1>
  <p>Random company description</p>
  <table><tr><td>Issue Size</td><td>999 Crore</td></tr></table>
</body></html>"""

result_null = parse_detail_page(NO_MATCH_HTML, ipo_name="Fusion Klassroom")
check("failed scoping: issue_size is None (not 999)", result_null['issue_size'], None)
check("failed scoping: about is None", result_null['about'], None)
check("failed scoping: lot_size is None", result_null['lot_size'], None)

# ---------------------------------------------------------------------------
# Test 5: extract_sector_from_text
# ---------------------------------------------------------------------------
print("\n=== Test 5: sector extraction (curated keywords, not regex) ===")

check("EdTech → Education", extract_sector_from_text("Fusion Klassroom is an EdTech platform"), "Education")
check("manufacturing → Manufacturing", extract_sector_from_text("Company is engaged in manufacturing of auto components"), "Manufacturing")
check("solar → Energy", extract_sector_from_text("Juniper Green Energy produces solar power"), "Energy")
check("pharma → Healthcare", extract_sector_from_text("Q-Line Biotech is engaged in pharma"), "Healthcare")
check("hygiene → Consumer", extract_sector_from_text("H.R. Hygiene Products manufactures hygiene products"), "Consumer")
check("Research Driven → None (not a sector)", extract_sector_from_text("Research Driven Technology"), None)
check("empty string → None", extract_sector_from_text(""), None)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed")
if FAIL == 0:
    print("ALL TESTS PASSED — scraper fix is verified.")
else:
    print(f"ATTENTION: {FAIL} test(s) failed — review before running the scraper.")
print('='*50)
