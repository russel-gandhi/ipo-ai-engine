import pytest
from backend.src.allotment.engine import (
    calculate_allotment_engine,
    calculate_minimum_allotment_draw_probability
)
from backend.src.allotment.regimes import resolve_ipo_regime_id, get_applicable_rule

# --- Regulatory Fixtures ---

@pytest.fixture
def fixture_mainboard_post_2022():
    return {
        "name": "Modern Energy Ltd",
        "exchange": "NSE, BSE",
        "is_sme": False,
        "open_date": "2024-05-15",
        "close_date": "2024-05-18",
        "lot_size": 100,
        "price_band": 150.0,
        "sub_retail": 3.2,
        "sub_nii": 15.4
    }

# --- 1. Primitive Unit Tests ---

def test_primitive_calculate_minimum_allotment_draw_probability():
    # 1000 shares quota, 100 per lot => 10 available allotments
    # 20 valid applications => 10/20 = 50%
    assert calculate_minimum_allotment_draw_probability(1000, 100, 20) == 50.0
    # 10 allotments, 10 apps => 100%
    assert calculate_minimum_allotment_draw_probability(1000, 100, 10) == 100.0
    # 10 allotments, 5 apps => 100%
    assert calculate_minimum_allotment_draw_probability(1000, 100, 5) == 100.0
    # Zero or invalid inputs => 0.0
    assert calculate_minimum_allotment_draw_probability(0, 100, 20) == 0.0

# --- 2. Category Amount Boundary Tests (₹2L and ₹10L Boundaries) ---

def test_category_boundary_exact_200k():
    res = calculate_allotment_engine({
        "category": "sNII",
        "applied_amount": 200000.0,
        "ipo_data": {"name": "Boundary Test", "is_sme": False, "open_date": "2024-05-15"}
    })
    assert res.category == "sNII"

def test_category_boundary_200k_plus_1():
    res = calculate_allotment_engine({
        "category": "sNII",
        "applied_amount": 200001.0,
        "ipo_data": {"name": "Boundary Test", "is_sme": False, "open_date": "2024-05-15"}
    })
    assert res.category == "sNII"

def test_category_boundary_exact_1M():
    res = calculate_allotment_engine({
        "category": "sNII",
        "applied_amount": 1000000.0,
        "ipo_data": {"name": "Boundary Test", "is_sme": False, "open_date": "2024-05-15"}
    })
    assert res.category == "sNII"

def test_category_boundary_1M_plus_1_transitions_to_bnii():
    res = calculate_allotment_engine({
        "category": "sNII",
        "applied_amount": 1000001.0,
        "ipo_data": {"name": "Boundary Test", "is_sme": False, "open_date": "2024-05-15"}
    })
    assert res.category == "bNII"

# --- 3. Applications vs Available Allotments Boundary Tests ---

def test_applications_one_fewer_than_allotments():
    # Quota 800 shares, min lot 100 => 8 allotments available. Apps = 7.
    res = calculate_allotment_engine({
        "category": "RETAIL",
        "ipo_data": {
            "name": "App Boundary Ltd",
            "is_sme": False,
            "open_date": "2024-05-15",
            "lot_size": 100,
            "retail_shares_quota": 800,
            "retail_gross_applications": 7
        }
    })
    assert res.probability_pct == 100.0
    assert res.calculation_status == "EXACT"

def test_applications_equal_to_allotments():
    # Quota 800 shares, min lot 100 => 8 allotments available. Apps = 8.
    res = calculate_allotment_engine({
        "category": "RETAIL",
        "ipo_data": {
            "name": "App Boundary Ltd",
            "is_sme": False,
            "open_date": "2024-05-15",
            "lot_size": 100,
            "retail_shares_quota": 800,
            "retail_gross_applications": 8
        }
    })
    assert res.probability_pct == 100.0
    assert res.calculation_status == "EXACT"

def test_applications_one_more_than_allotments():
    # Quota 800 shares, min lot 100 => 8 allotments available. Apps = 9. Prob = 8/9 = 88.89%
    res = calculate_allotment_engine({
        "category": "RETAIL",
        "ipo_data": {
            "name": "App Boundary Ltd",
            "is_sme": False,
            "open_date": "2024-05-15",
            "lot_size": 100,
            "retail_shares_quota": 800,
            "retail_gross_applications": 9
        }
    })
    assert res.probability_pct == round((8 / 9) * 100.0, 2)
    assert res.calculation_status == "EXACT"

# --- 4. Mathematical Invariant & Property Tests ---

def test_invariant_probability_bounds(fixture_mainboard_post_2022):
    res = calculate_allotment_engine({
        "category": "RETAIL",
        "ipo_data": fixture_mainboard_post_2022
    })
    if res.probability_pct is not None:
        assert 0.0 <= res.probability_pct <= 100.0
    if res.expected_lots is not None:
        assert res.expected_lots >= 0.0

def test_invariant_exact_probability_null_if_inputs_missing(fixture_mainboard_post_2022):
    res = calculate_allotment_engine({
        "category": "RETAIL",
        "ipo_data": fixture_mainboard_post_2022 # valid_application_count missing
    })
    assert res.probability_pct is None
    assert res.calculation_status == "INSUFFICIENT_APPLICATION_DATA"
    assert res.calculation_data_complete is False
    assert "valid_application_count" in res.audit_trace.missing_inputs

def test_invariant_share_sub_change_does_not_change_probability_when_app_counts_unknown():
    res1 = calculate_allotment_engine({
        "category": "RETAIL",
        "ipo_data": {"name": "Sub Test", "is_sme": False, "open_date": "2024-05-15", "sub_retail": 10.0}
    })
    res2 = calculate_allotment_engine({
        "category": "RETAIL",
        "ipo_data": {"name": "Sub Test", "is_sme": False, "open_date": "2024-05-15", "sub_retail": 100.0}
    })
    # Both must be null and never fabricate a probability from 10x or 100x
    assert res1.probability_pct is None
    assert res2.probability_pct is None
    assert res1.calculation_status == "INSUFFICIENT_APPLICATION_DATA"
    assert res2.calculation_status == "INSUFFICIENT_APPLICATION_DATA"

def test_invariant_final_basis_of_allotment_only_when_published():
    res = calculate_allotment_engine({
        "category": "RETAIL",
        "ipo_data": {
            "name": "BoA Test",
            "is_sme": False,
            "open_date": "2024-05-15",
            "basis_of_allotment": {
                "is_published": True,
                "published_at": "2024-05-20",
                "allotment_ratio_by_category": {"retail": 0.4}
            }
        }
    })
    assert res.calculation_status == "FINAL_BASIS_OF_ALLOTMENT"
    assert res.probability_pct == 40.0

# --- 5. Operative Date Transition Tests ---

def test_mainboard_transition_dates():
    # Pre April 1, 2022
    pre = {"name": "Pre 2022", "is_sme": False, "open_date": "2022-03-31"}
    post = {"name": "Post 2022", "is_sme": False, "open_date": "2022-04-01"}
    assert resolve_ipo_regime_id(pre) == "MAINBOARD_PRE_2022"
    assert resolve_ipo_regime_id(post) == "MAINBOARD_POST_2022"

def test_sme_transition_dates():
    # Pre Jan 1, 2025
    sme_old = {"name": "SME Old", "is_sme": True, "open_date": "2024-12-31"}
    sme_new = {"name": "SME 2025", "is_sme": True, "open_date": "2025-01-01"}
    assert resolve_ipo_regime_id(sme_old) == "SME_OLD_FRAMEWORK"
    assert resolve_ipo_regime_id(sme_new) == "SME_2025_FRAMEWORK"
