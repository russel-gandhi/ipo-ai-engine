from backend.src.allotment.calculator import calculate_sebi_allotment_odds

ipo_data = {
    "retail_shares_quota": 0,
    "shni_shares_quota": 100000, 
    "bhni_shares_quota": 0,
    "qib_shares_quota": 0,
    "employee_shares_quota": 0,
    "qib_subscription_multiple": 1.5,
    "employee_subscription_multiple": 1.5,
    "retail_gross_applications": 0,
    # For an 8.33x subscription in sHNI, if quota is 100000 shares and min lot is 14 lots * 30 shares = 420 shares:
    # Available lots = 100000 // 420 = 238 lots
    # Gross applications to get 8.33x = 238 * 8.33 = 1982 applications
    "shni_gross_applications": 1982,
    "min_lot_shares_retail": 30,
    "min_lot_shares_shni": 420, # 14 lots * 30 shares
    "min_lot_shares_bhni": 420 
}

# The user applied for 14 lots (₹203,700)
result = calculate_sebi_allotment_odds("ABCDE1234F", "sHNI", 203700, ipo_data)
print(result)
