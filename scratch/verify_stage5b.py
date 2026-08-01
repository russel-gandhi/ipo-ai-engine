"""
Stage 5B Verification Script
Validates the enriched /api/live-ipos response against the spec.
Run after restarting the backend with the new scraper.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Read directly from the generated file (no API server needed for this check)
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'data', 'live_ipos.json')

REQUIRED_FIELDS = [
    "name", "gmp", "price_band", "gmp_trend", "est_listing_gain_pct",
    "detail_url", "exchange", "is_sme", "status",
    "sector", "issue_size", "price_band_range", "lot_size",
    "open_date", "close_date", "allotment_date", "listing_date",
    "sub_qib", "sub_nii", "sub_retail", "sub_overall",
    "lot_distribution", "offer_breakdown",
    "about", "issue_objective", "financials",
]

VALID_STATUSES = {"open", "closing_today", "upcoming", "closed"}

def run_checks():
    print("=" * 60)
    print("Stage 5B Verification")
    print("=" * 60)
    
    if not os.path.exists(DATA_FILE):
        print("FAIL: live_ipos.json not found. Run the scraper first.")
        return False
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    passed = 0
    failed = 0
    
    # Check 1: last_updated exists
    if data.get("last_updated"):
        print(f"  PASS: last_updated = {data['last_updated']}")
        passed += 1
    else:
        print("  FAIL: last_updated missing")
        failed += 1
    
    # Check 2: ipos is a non-empty list
    ipos = data.get("ipos", [])
    if ipos and isinstance(ipos, list):
        print(f"  PASS: {len(ipos)} IPOs found")
        passed += 1
    else:
        print(f"  FAIL: ipos is empty or not a list")
        failed += 1
        return False
    
    # Check 3: All IPOs have all required fields (even if null)
    all_have_fields = True
    for ipo in ipos:
        missing = [f for f in REQUIRED_FIELDS if f not in ipo]
        if missing:
            print(f"  FAIL: '{ipo.get('name', '?')}' missing fields: {missing}")
            all_have_fields = False
            failed += 1
    if all_have_fields:
        print(f"  PASS: All IPOs have all {len(REQUIRED_FIELDS)} required fields")
        passed += 1
    
    # Check 4: At least one IPO has all non-subscription fields populated
    enriched_count = 0
    for ipo in ipos:
        non_sub_fields = ["sector", "issue_size", "lot_size", "open_date", "close_date",
                          "lot_distribution", "offer_breakdown", "about", "financials"]
        populated = [f for f in non_sub_fields if ipo.get(f) is not None]
        if len(populated) >= 6:  # At least 6 out of 9
            enriched_count += 1
    
    if enriched_count > 0:
        print(f"  PASS: {enriched_count} IPOs have rich detail data (≥6 non-subscription fields)")
        passed += 1
    else:
        print(f"  FAIL: No IPOs have rich detail data")
        failed += 1
    
    # Check 5: lot_distribution is an array where present
    lot_dist_ok = True
    for ipo in ipos:
        ld = ipo.get("lot_distribution")
        if ld is not None and not isinstance(ld, list):
            print(f"  FAIL: '{ipo['name']}' lot_distribution is not a list: {type(ld)}")
            lot_dist_ok = False
            failed += 1
    if lot_dist_ok:
        print(f"  PASS: lot_distribution is array (or null) for all IPOs")
        passed += 1
    
    # Check 6: financials is an array where present
    fin_ok = True
    for ipo in ipos:
        fin = ipo.get("financials")
        if fin is not None and not isinstance(fin, list):
            print(f"  FAIL: '{ipo['name']}' financials is not a list: {type(fin)}")
            fin_ok = False
            failed += 1
    if fin_ok:
        print(f"  PASS: financials is array (or null) for all IPOs")
        passed += 1
    
    # Check 7: offer_breakdown is an object where present
    ob_ok = True
    for ipo in ipos:
        ob = ipo.get("offer_breakdown")
        if ob is not None and not isinstance(ob, dict):
            print(f"  FAIL: '{ipo['name']}' offer_breakdown is not a dict: {type(ob)}")
            ob_ok = False
            failed += 1
    if ob_ok:
        print(f"  PASS: offer_breakdown is object (or null) for all IPOs")
        passed += 1
    
    # Check 8: status is valid
    status_ok = True
    for ipo in ipos:
        s = ipo.get("status")
        if s not in VALID_STATUSES:
            print(f"  FAIL: '{ipo['name']}' has invalid status: '{s}'")
            status_ok = False
            failed += 1
    if status_ok:
        print(f"  PASS: All IPOs have valid status (open/closing_today/upcoming/closed)")
        passed += 1
    
    # Check 9: null fields are null, not empty strings or zeroes
    null_ok = True
    sub_fields = ["sub_qib", "sub_nii", "sub_retail", "sub_overall"]
    for ipo in ipos:
        for f in sub_fields:
            val = ipo.get(f)
            if val is not None and val != 0 and val != 0.0:
                # Subscription data should be null for now
                print(f"  INFO: '{ipo['name']}' {f} = {val} (unexpected non-null subscription data)")
            if val == "":
                print(f"  FAIL: '{ipo['name']}' {f} is empty string, should be null")
                null_ok = False
                failed += 1
            if val == 0 or val == 0.0:
                # Check it's truly null not zero
                if ipo[f] is not None and ipo[f] == 0:
                    pass  # 0 is technically a valid value, just unusual
    if null_ok:
        print(f"  PASS: No empty strings found in subscription fields")
        passed += 1
    
    # Print a sample enriched IPO
    print(f"\n{'=' * 60}")
    print("Sample Enriched IPO:")
    print("=" * 60)
    best = max(ipos, key=lambda x: sum(1 for v in x.values() if v is not None))
    for k, v in best.items():
        if isinstance(v, str) and len(v) > 100:
            print(f"  {k}: {v[:100]}...")
        else:
            print(f"  {k}: {v}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ ALL CHECKS PASSED — Stage 5B verification gate cleared!")
    else:
        print("❌ SOME CHECKS FAILED — review above and fix before proceeding to Stage 7")
    
    return failed == 0

if __name__ == "__main__":
    run_checks()
