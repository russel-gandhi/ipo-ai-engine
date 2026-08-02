import json
import sys
from pathlib import Path

DEMO_IPO_NAMES = [
    "Juniper Green Energy",       # Current Mainboard IPO
    "G.V. Electricals",           # Current SME IPO
    "H.R. Hygiene Products",      # Target Closed SME IPO
    "Zaggle Prepaid Ocean Services"# Historical IPO with Official BoA
]

def validate_demo_ipos():
    data_path = Path("backend/src/data/live_ipos.json")
    if not data_path.exists():
        print(f"[FAIL] File not found: {data_path}")
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    ipos_by_name = {ipo["name"]: ipo for ipo in dataset.get("ipos", [])}
    
    all_passed = True
    print("====================================")
    print("IPO-AI DEMO DATA VALIDATION REPORT")
    print("====================================\n")

    for name in DEMO_IPO_NAMES:
        print(f"--- Validating: {name} ---")
        ipo = ipos_by_name.get(name)
        if not ipo:
            print(f"[FAIL] Missing target demo IPO in dataset: {name}")
            all_passed = False
            continue

        ipo_passed = True

        # 1. Identity & Classification
        if not ipo.get("exchange") or not ipo.get("issue_type"):
            print("  [FAIL] Missing identity/exchange/issue_type fields.")
            ipo_passed = False
        else:
            print(f"  [PASS] Identity ({ipo.get('exchange')}, {ipo.get('issue_type')})")

        # 2. Pricing & Lots Reconciliation
        lot_size = ipo.get("lot_size", 0)
        price = ipo.get("price_band") or ipo.get("price_high") or 0
        min_inv = ipo.get("min_investment") or (lot_size * price)
        if lot_size <= 0 or price <= 0 or min_inv <= 0:
            print("  [FAIL] Invalid pricing/lot distribution.")
            ipo_passed = False
        else:
            print(f"  [PASS] Issue details (Lot: {lot_size}, Price: Rs.{price}, Min Inv: Rs.{min_inv})")

        # 3. Financials Period Tagging
        fin = ipo.get("financials")
        fin_obj = fin[0] if isinstance(fin, list) and len(fin) > 0 else (fin if isinstance(fin, dict) else {})
        
        if not fin_obj or not fin_obj.get("period"):
            print("  [FAIL] Financial period tag missing.")
            ipo_passed = False
        elif fin_obj.get("revenue_from_operations") is None and fin_obj.get("total_revenue") is None:
            print("  [FAIL] Missing revenue metrics.")
            ipo_passed = False
        else:
            print(f"  [PASS] Financials (Period: {fin_obj.get('period')}, Rev Ops: Rs.{fin_obj.get('revenue_from_operations')}Cr, Total Rev: Rs.{fin_obj.get('total_revenue')}Cr)")

        # 4. Subscription Data & Provenance
        if ipo.get("status") in ("open", "closed"):
            sub_ts = ipo.get("subscription_updated_at")
            if not sub_ts:
                print("  [FAIL] Missing subscription timestamp.")
                ipo_passed = False
            else:
                print(f"  [PASS] Subscription provenance (Updated: {sub_ts})")

        # 5. BoA Specific Validation for Zaggle
        if "Zaggle" in name:
            boa = ipo.get("basis_of_allotment", {})
            if not boa.get("is_published") or not boa.get("allotment_ratio_by_category"):
                print("  [FAIL] Historical BoA missing or unpublished.")
                ipo_passed = False
            else:
                print("  [PASS] Official Basis of Allotment published and verified.")

        if ipo_passed:
            print(f"Result: {name} -> PASSED\n")
        else:
            print(f"Result: {name} -> FAILED\n")
            all_passed = False

    print("====================================")
    if all_passed:
        print("DEMO STATUS: READY")
        print("====================================")
        sys.exit(0)
    else:
        print("DEMO STATUS: NOT READY")
        print("====================================")
        sys.exit(1)

if __name__ == "__main__":
    validate_demo_ipos()
