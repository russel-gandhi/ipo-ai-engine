import pytest
from backend.src.allotment.calculator import calculate_sebi_allotment_odds, validate_pan

def test_pan_validation():
    # Valid PAN
    assert validate_pan("ABCDE1234F") == "ABCDE1234F"
    assert validate_pan(" abcde1234f ") == "ABCDE1234F"
    
    # Invalid PANs
    with pytest.raises(ValueError, match="Invalid PAN layout"):
        validate_pan("ABCD12345F")
    
    with pytest.raises(ValueError, match="Invalid PAN layout"):
        validate_pan("12345ABCDE")

def test_retail_oversubscribed_with_spillover():
    ipo_data = {
        "retail_shares_quota": 100000,
        "shni_shares_quota": 50000,
        "bhni_shares_quota": 50000,
        "qib_shares_quota": 200000,
        "employee_shares_quota": 10000,
        "qib_subscription_multiple": 0.5, # Undersubscribed (100k shares spillover)
        "employee_subscription_multiple": 0.5, # Undersubscribed (5k shares spillover)
        "retail_gross_applications": 50000,
        "min_lot_shares_retail": 10
    }
    
    # Adjusted retail shares = 100k + 100k + 5k = 205k
    # L_R = floor(205000 / 10) = 20500 lots
    # N_R = 50000 * 0.97 = 48500 unique valid apps
    # P_R = (20500 / 48500) * 100 = 42.268%
    
    res = calculate_sebi_allotment_odds("ABCDE1234F", "Retail", 15000, ipo_data)
    
    assert res["probability_pct"] == 42.27
    assert res["masked_pan"] == "⁕⁕⁕⁕⁕⁕234F"
    assert "Applying for multiple lots" in res["guardrail"]
    assert "volatile memory" in res["privacy_note"]
    
    print("Test Retail Oversubscribed with Spillover Passed:", res["probability_pct"])

def test_qib_always_100_percent():
    res = calculate_sebi_allotment_odds("QWERT9876A", "QIB", 5000000, {})
    assert res["probability_pct"] == 100.0
    assert "strictly proportional" in res["explain_text"]

def test_invalid_pan_returns_error():
    res = calculate_sebi_allotment_odds("INVALIDPAN", "Retail", 15000, {})
    assert "error" in res
    assert "Invalid PAN layout" in res["error"]

if __name__ == "__main__":
    test_pan_validation()
    test_retail_oversubscribed_with_spillover()
    test_qib_always_100_percent()
    test_invalid_pan_returns_error()
