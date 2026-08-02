import math
from typing import Dict, Any, Optional, List
from backend.src.allotment.schemas import EnrichedAllotmentResponse, AllotmentAuditTrace, BasisOfAllotmentData
from backend.src.allotment.regimes import get_applicable_rule, resolve_ipo_regime_id

def validate_pan(pan: str) -> str:
    """Validates PAN layout standard format (5 letters, 4 numbers, 1 letter)."""
    import re
    cleaned = str(pan).strip().upper()
    if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", cleaned):
        raise ValueError("Invalid PAN format. Must be 5 letters, 4 numbers, 1 letter (e.g. ABCDE1234F).")
    return cleaned

def mask_pan(pan: str) -> str:
    if len(pan) >= 4:
        return "⁕⁕⁕⁕⁕⁕" + pan[-4:]
    return "⁕⁕⁕⁕⁕⁕⁕⁕⁕⁕"

def calculate_minimum_allotment_draw_probability(
    quota_shares: int,
    min_lot_shares: int,
    gross_applications: int
) -> float:
    """
    NAMED CALCULATION PRIMITIVE:
    Computes exact minimum-allotment draw-of-lots probability per SEBI ICDR guidelines.
    Invoked ONLY when the resolved regulatory rule explicitly requires draw of lots
    for minimum allotments.
    
    Formula:
    L = floor(quota_shares / min_lot_shares)
    P = min(100.0, (L / gross_applications) * 100.0)
    """
    if quota_shares <= 0 or min_lot_shares <= 0 or gross_applications <= 0:
        return 0.0
    
    available_min_allotments = math.floor(quota_shares / min_lot_shares)
    if available_min_allotments <= 0:
        return 0.0
        
    if gross_applications <= available_min_allotments:
        return 100.0
        
    prob = (available_min_allotments / gross_applications) * 100.0
    return round(min(100.0, max(0.0, prob)), 2)


def calculate_allotment_engine(request_data: Dict[str, Any]) -> EnrichedAllotmentResponse:
    """
    Centralized allotment engine designed to apply the applicable SEBI/exchange allotment framework
    using verified regulatory rules and available IPO-specific data.
    """
    category = request_data.get("category", "RETAIL").strip()
    ipo = request_data.get("ipo_data") or request_data
    
    pan = request_data.get("pan", "ABCDE1234F")
    try:
        clean_pan = validate_pan(pan)
    except ValueError:
        clean_pan = "ABCDE1234F"

    # Resolve regulatory regime and rule
    regime_id = resolve_ipo_regime_id(ipo)
    rule = get_applicable_rule(ipo, category)
    rule_known = True if rule else False

    # Check Basis of Allotment ingestion
    boa_raw = ipo.get("basis_of_allotment") or request_data.get("basis_of_allotment")
    boa = BasisOfAllotmentData(**boa_raw) if isinstance(boa_raw, dict) else None

    # Inputs
    lot_size = int(ipo.get("lot_size") or 100)
    cutoff_price = float(ipo.get("price_band") or ipo.get("cutoff_price") or 100.0)
    num_pans = int(request_data.get("num_pans") or 1)
    applied_lots = int(request_data.get("applied_lots") or 1)
    applied_amount = float(request_data.get("applied_amount") or (applied_lots * lot_size * cutoff_price))
    
    cat_upper = category.upper()

    # Category Boundary Checks (₹2L and ₹10L thresholds)
    if regime_id == "MAINBOARD_POST_2022":
        if "SNII" in cat_upper or "SHNI" in cat_upper:
            if applied_amount > 1000000.0:
                cat_upper = "BNII"
                category = "bNII"
                rule = get_applicable_rule(ipo, "bNII")
        elif "BNII" in cat_upper or "BHNI" in cat_upper:
            if applied_amount <= 1000000.0:
                cat_upper = "SNII"
                category = "sNII"
                rule = get_applicable_rule(ipo, "sNII")
    
    # Category subscription data (Factual Demand Multiples)
    sub_retail = ipo.get("sub_retail")
    sub_nii = ipo.get("sub_nii")
    sub_qib = ipo.get("sub_qib")
    
    share_sub_multiple = None
    if "RETAIL" in cat_upper or "INDIVIDUAL" in cat_upper:
        share_sub_multiple = float(sub_retail) if sub_retail is not None else None
    elif "SNII" in cat_upper or "SHNI" in cat_upper or "BNII" in cat_upper or "BHNI" in cat_upper or "NII" in cat_upper:
        share_sub_multiple = float(sub_nii) if sub_nii is not None else None
    elif "QIB" in cat_upper:
        share_sub_multiple = float(sub_qib) if sub_qib is not None else None

    # Extract inputs available vs required for probability
    gross_apps = ipo.get(f"{category.lower()}_gross_applications") or ipo.get("gross_applications")
    quota_shares = ipo.get(f"{category.lower()}_shares_quota") or ipo.get("quota_shares")
    
    # If BoA has published valid applications for category
    if boa and boa.is_published and boa.valid_applications_by_category:
        for k, v in boa.valid_applications_by_category.items():
            if category.lower() in k.lower():
                gross_apps = v
                break

    # Determine required vs available inputs
    required_inputs = list(rule.required_inputs_for_probability)
    available_inputs = []
    
    if quota_shares is not None:
        available_inputs.append("category_quota_shares")
    if lot_size is not None:
        available_inputs.append("minimum_allotment_shares")
    if gross_apps is not None:
        available_inputs.append("valid_application_count")
    if share_sub_multiple is not None:
        available_inputs.append("shares_bid")
        available_inputs.append("shares_offered")
        available_inputs.append("total_shares_bid")
        
    missing_inputs = [i for i in required_inputs if i not in available_inputs]
    calculation_data_complete = (len(missing_inputs) == 0)

    steps = []
    assumptions = []
    limitations = []

    steps.append(f"1. Identified Regulatory Regime: {regime_id} ({rule.board_type}, {rule.issue_type}).")
    steps.append(f"2. Applicable SEBI Rule: {rule.rule_id} — {rule.regulation_reference}.")
    steps.append(f"3. Allocation Method: {rule.allocation_method}.")
    
    if boa and boa.is_published:
        steps.append(f"4. Authoritative Basis of Allotment published at {boa.published_at or 'Registrar/Exchange'}.")
    else:
        steps.append("4. Operating in PRE_ALLOTMENT mode (Basis of Allotment not yet published).")

    exact_prob = None
    est_prob = None
    app_sub_multiple = None
    calc_status = "INSUFFICIENT_APPLICATION_DATA"
    status_label = "Exact Allotment Odds Unavailable"
    allotment_regime_name = rule.allocation_method
    explain_text = ""
    guardrail_msg = ""

    expected_shares = None
    expected_lots = None
    expected_val = None

    # CASE A: Final Basis of Allotment published
    if boa and boa.is_published and category.lower() in [k.lower() for k in boa.allotment_ratio_by_category.keys()]:
        for cat_k, ratio_v in boa.allotment_ratio_by_category.items():
            if category.lower() in cat_k.lower():
                exact_prob = round(ratio_v * 100.0, 2)
                calc_status = "FINAL_BASIS_OF_ALLOTMENT"
                status_label = "Final Allotment Odds (Basis of Allotment)"
                allotment_regime_name = "Final Basis of Allotment"
                explain_text = f"Official Basis of Allotment published. Final allotment ratio for {category} is {exact_prob}%."
                expected_lots = round(applied_lots * ratio_v, 2)
                calculation_data_complete = True
                break

    # CASE B: Evaluated from application-wise & quota data under SEBI rules
    elif calculation_data_complete and rule.allocation_method == "MINIMUM_ALLOTMENT_THEN_LOTTERY":
        min_lot_shares = lot_size
        if "SNII" in cat_upper or "SHNI" in cat_upper:
            min_lot_shares = int(ipo.get("min_lot_shares_shni") or (14 * lot_size))
        elif "BNII" in cat_upper or "BHNI" in cat_upper:
            min_lot_shares = int(ipo.get("min_lot_shares_bhni") or (68 * lot_size))

        if quota_shares and min_lot_shares and gross_apps:
            available_min_allotments = math.floor(quota_shares / min_lot_shares)
            app_sub_multiple = round(gross_apps / available_min_allotments, 2) if available_min_allotments > 0 else None
            
            steps.append(f"5. Available Minimum Allotments: {available_min_allotments} (Quota Shares: {quota_shares}, Min Lot: {min_lot_shares}).")
            steps.append(f"6. Total Valid Applications: {gross_apps}. Application Oversubscription Multiple: {app_sub_multiple}x.")
            
            # CALL NAMED CALCULATION PRIMITIVE
            exact_prob = calculate_minimum_allotment_draw_probability(
                quota_shares=quota_shares,
                min_lot_shares=min_lot_shares,
                gross_applications=gross_apps
            )
            
            steps.append(f"7. Executed primitive `calculate_minimum_allotment_draw_probability`: Result = {exact_prob}%.")

            if gross_apps <= available_min_allotments:
                calc_status = "EXACT"
                status_label = "Calculated Allotment Probability"
                allotment_regime_name = "Full Allotment Eligibility"
                explain_text = "Eligible for full allotment subject to application validity, availability, final issue price/bid conditions and applicable issue terms."
                expected_lots = 1.0
            else:
                calc_status = "EXACT"
                status_label = "Calculated Allotment Probability"
                allotment_regime_name = "Draw of Lots / SEBI Lottery"
                explain_text = f"Application-wise demand ({gross_apps} valid apps) exceeds available minimum allotments ({available_min_allotments}). SEBI draw of lots applies. Calculated probability is {exact_prob}%."
                expected_lots = round(exact_prob / 100.0, 4)
                guardrail_msg = "Applying for multiple lots on the same PAN does NOT increase your allotment probability."

    # CASE C: Undersubscribed Share-wise case (Sub <= 1.0x)
    elif share_sub_multiple is not None and share_sub_multiple <= 1.0:
        exact_prob = 100.0
        calc_status = "EXACT"
        status_label = "Calculated Allotment Probability"
        allotment_regime_name = "Full Allotment Eligibility"
        explain_text = f"Share subscription is {share_sub_multiple:.2f}x (<= 1.0x). Eligible for full allotment subject to application validity, availability, final issue price/bid conditions and applicable issue terms."
        expected_lots = float(applied_lots)
        calculation_data_complete = True

    # CASE D: Data Incomplete (Missing Application Count or BoA)
    else:
        calc_status = "INSUFFICIENT_APPLICATION_DATA"
        status_label = "Exact Allotment Odds Unavailable"
        exact_prob = None
        est_prob = None
        expected_lots = None
        explain_text = f"Exact allotment odds unavailable. We know how SEBI allotment works for {category} under {rule.rule_id}, but valid application counts are missing."
        limitations.append(f"Missing required inputs for calculation: {', '.join(missing_inputs)}.")
        limitations.append("Share subscription multiple alone is insufficient to calculate allotment probability or expected lots.")

    # Calculate expected values if expected_lots is validly determined
    if expected_lots is not None:
        expected_shares = round(expected_lots * lot_size, 1)
        expected_val = round(expected_shares * cutoff_price, 2)

    # Family PAN probability calculation (ONLY if single probability is legitimately known)
    prob_at_least_one = None
    if exact_prob is not None:
        p_unit = exact_prob / 100.0
        prob_at_least_one = round(1.0 - math.pow(1.0 - p_unit, num_pans), 4) if p_unit < 1.0 else 1.0
        assumptions.append(f"Estimated probability of at least one successful application models {num_pans} legally distinct PAN holders and assumes independent draw outcomes.")

    audit_trace = AllotmentAuditTrace(
        regime_id=regime_id,
        rule_id=rule.rule_id,
        rule_version="2025.3",
        board_type=rule.board_type,
        issue_type=rule.issue_type,
        effective_period=f"{rule.effective_from} to {rule.effective_until or 'Present'}",
        category=category,
        source_type=rule.source_type,
        authority_level=rule.authority_level,
        rule_known=rule_known,
        calculation_data_complete=calculation_data_complete,
        required_inputs=required_inputs,
        available_inputs=available_inputs,
        missing_inputs=missing_inputs,
        inputs_used={
            "pan": mask_pan(clean_pan),
            "category": category,
            "num_pans": num_pans,
            "applied_lots": applied_lots,
            "lot_size": lot_size,
            "cutoff_price": cutoff_price,
            "sub_retail": sub_retail,
            "sub_nii": sub_nii,
            "sub_qib": sub_qib,
            "gross_applications": gross_apps,
            "quota_shares": quota_shares
        },
        category_quota_shares=quota_shares,
        minimum_allotment_shares=lot_size,
        minimum_allotment_lots=1,
        share_subscription_multiple=share_sub_multiple,
        application_oversubscription_multiple=app_sub_multiple,
        allocation_method=rule.allocation_method,
        calculation_steps=steps,
        exact_probability=exact_prob,
        estimated_probability=est_prob,
        status=calc_status,
        expected_allotment_shares=expected_shares,
        expected_allotment_lots=expected_lots,
        assumptions=assumptions,
        limitations=limitations,
        regulation_reference=rule.regulation_reference,
        source_url=rule.source_url,
        confidence="HIGH" if calc_status in ("EXACT", "FINAL_BASIS_OF_ALLOTMENT") else "RULE_BASED"
    )

    return EnrichedAllotmentResponse(
        category=category,
        masked_pan=mask_pan(clean_pan),
        rule_known=rule_known,
        calculation_data_complete=calculation_data_complete,
        calculation_status=calc_status,
        status_label=status_label,
        probability_pct=exact_prob,
        estimated_probability_pct=est_prob,
        probability_at_least_one_lot=prob_at_least_one,
        share_subscription_multiple=share_sub_multiple,
        application_oversubscription_multiple=app_sub_multiple,
        expected_lots=expected_lots,
        expected_shares=expected_shares,
        expected_value=expected_val,
        allotment_regime=allotment_regime_name,
        explain_text=explain_text,
        guardrail=guardrail_msg,
        audit_trace=audit_trace
    )
