import pytest
from backend.src.allotment.calculator import calculate_allotment_odds

def test_calculate_allotment_odds_undersubscribed():
    # If subscription is 0.5x, odds should be 100%
    res = calculate_allotment_odds("Retail", 1, 0.5)
    assert res["probability_pct"] == 100.0
    assert res["lots_applied"] == 1

def test_calculate_allotment_odds_indo_mim():
    # Indo-MIM Limited actual current numbers: ~3.07x overall subscription
    res = calculate_allotment_odds("Retail", 1, 3.07)
    
    # 1 / 3.07 = 0.3257 -> ~32.57%
    assert res["probability_pct"] == 32.57
    assert "3.07x subscription" in res["explain_text"]
    assert "roughly 32.57%" in res["explain_text"]
    assert "33 out of 100 raffle tickets" in res["explain_text"]
    assert "approximates the real SEBI lottery algorithm" in res["explain_text"]
    
    print("Indo-MIM Retail Test Passed:", res)

def test_calculate_allotment_odds_highly_oversubscribed():
    # e.g., Vibhor Steel Tubes Retail was 188.17x
    res = calculate_allotment_odds("Retail", 1, 188.17)
    # 1 / 188.17 = 0.00531 -> 0.53%
    assert res["probability_pct"] == 0.53
    print("Vibhor Steel Tubes Retail Test Passed:", res)

if __name__ == "__main__":
    test_calculate_allotment_odds_undersubscribed()
    test_calculate_allotment_odds_indo_mim()
    test_calculate_allotment_odds_highly_oversubscribed()
