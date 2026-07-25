import re
import math

def validate_pan(pan: str) -> str:
    """
    Validates and cleans a PAN (Permanent Account Number).
    Format: 5 uppercase letters, 4 numeric digits, 1 uppercase letter.
    """
    cleaned_pan = str(pan).strip().upper()
    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
    
    if not re.match(pattern, cleaned_pan):
        raise ValueError("Invalid PAN layout. Ensure your input matches the standard Indian PAN format: 5 letters, 4 numbers, and 1 letter (e.g., ABCDE1234F).")
    
    return cleaned_pan


def mask_pan(pan: str) -> str:
    """
    Masks the PAN for UI display. Only the last 4 characters are openly visible.
    """
    if len(pan) >= 4:
        return "⁕⁕⁕⁕⁕⁕" + pan[-4:]
    return "⁕⁕⁕⁕⁕⁕⁕⁕⁕⁕"


def calculate_sebi_allotment_odds(
    pan: str,
    category: str,
    applied_amount: float,
    ipo_data: dict
) -> dict:
    """
    Calculates IPO allotment probabilities using SEBI allocation algorithms.
    
    ipo_data format:
    {
        "retail_shares_quota": int,
        "shni_shares_quota": int,
        "bhni_shares_quota": int,
        "qib_shares_quota": int,
        "employee_shares_quota": int,
        "qib_subscription_multiple": float,
        "employee_subscription_multiple": float,
        "retail_gross_applications": int,
        "shni_gross_applications": int,
        "bhni_gross_applications": int,
        "min_lot_shares_retail": int,
        "min_lot_shares_shni": int,
        "min_lot_shares_bhni": int
    }
    """
    # 1. Structural Validation
    try:
        clean_pan = validate_pan(pan)
    except ValueError as e:
        return {"error": str(e)}

    # Technical Rejection Buffer
    K_BUFFER = 0.03
    
    # 2. Compute Spillover
    spillover_shares = 0
    
    qib_sub = ipo_data.get("qib_subscription_multiple", 0)
    qib_quota = ipo_data.get("qib_shares_quota", 0)
    if qib_sub < 1.0:
        spillover_shares += qib_quota * (1.0 - qib_sub)
        
    emp_sub = ipo_data.get("employee_subscription_multiple", 0)
    emp_quota = ipo_data.get("employee_shares_quota", 0)
    if emp_sub < 1.0:
        spillover_shares += emp_quota * (1.0 - emp_sub)

    # Output defaults
    probability_pct = 0.0
    explain_text = ""
    guardrail_msg = ""
    
    if category == "Retail":
        original_retail = ipo_data.get("retail_shares_quota", 0)
        adjusted_retail_shares = original_retail + spillover_shares
        min_lot_shares = ipo_data.get("min_lot_shares_retail", 1)
        
        # Floor function for lots
        L_R = math.floor(adjusted_retail_shares / min_lot_shares)
        
        gross_apps = ipo_data.get("retail_gross_applications", 0)
        N_R = gross_apps * (1 - K_BUFFER)
        
        if N_R <= L_R:
            probability_pct = 100.0
        else:
            probability_pct = (L_R / N_R) * 100 if N_R > 0 else 100.0
            
        probability_pct = min(100.0, probability_pct)
        
        if N_R > L_R:
            guardrail_msg = "Applying for multiple lots on a single PAN does not increase your probability. The odds remain completely flat. Maximum reward if won is capped at 1 minimum lot."
            
        explain_text = (
            f"Based on SEBI lottery algorithms and current Retail subscriptions, "
            f"your estimated odds of getting exactly one lot are roughly {probability_pct:.2f}%. "
            f"Think of it like {round(probability_pct)} out of 100 unique applicants winning something."
        )

    elif category == "sHNI":
        shni_quota = ipo_data.get("shni_shares_quota", 0)
        min_lot_shares = ipo_data.get("min_lot_shares_shni", 1)
        
        L_sHNI = math.floor(shni_quota / min_lot_shares)
        gross_apps = ipo_data.get("shni_gross_applications", 0)
        N_sHNI = gross_apps * (1 - K_BUFFER)
        
        if N_sHNI <= L_sHNI:
            probability_pct = 100.0
        else:
            probability_pct = (L_sHNI / N_sHNI) * 100 if N_sHNI > 0 else 100.0
            
        probability_pct = min(100.0, probability_pct)
        
        if N_sHNI > L_sHNI:
            guardrail_msg = "Successful winners receive exactly the minimum sHNI lot size. Bidding deeper into the sHNI bracket does not increase lottery success rates if oversubscribed."

        explain_text = (
            f"Based on SEBI lottery algorithms for sHNI, "
            f"your estimated odds of an allotment are roughly {probability_pct:.2f}%."
        )

    elif category == "bHNI":
        bhni_quota = ipo_data.get("bhni_shares_quota", 0)
        min_lot_shares = ipo_data.get("min_lot_shares_bhni", 1)
        
        L_bHNI = math.floor(bhni_quota / min_lot_shares)
        gross_apps = ipo_data.get("bhni_gross_applications", 0)
        N_bHNI = gross_apps * (1 - K_BUFFER)
        
        if N_bHNI <= L_bHNI:
            probability_pct = 100.0
        else:
            probability_pct = (L_bHNI / N_bHNI) * 100 if N_bHNI > 0 else 100.0
            
        probability_pct = min(100.0, probability_pct)
        
        explain_text = (
            f"Based on SEBI lottery algorithms for bHNI, "
            f"your estimated odds of an allotment are roughly {probability_pct:.2f}%."
        )

    elif category == "QIB":
        # Proportional allocation
        probability_pct = 100.0
        explain_text = "QIB allocation is strictly proportional. You have a 100% probability of partial allotment subject to proportional scaling."

    return {
        "category": category,
        "masked_pan": mask_pan(clean_pan),
        "probability_pct": round(probability_pct, 2),
        "explain_text": explain_text,
        "guardrail": guardrail_msg,
        "privacy_note": "PAN data lives strictly in volatile memory and is never written to persistent storage."
    }

# Mock original function to remain compatible if imported loosely, but with warnings or simple passthrough
def calculate_allotment_odds(*args, **kwargs):
    raise DeprecationWarning("calculate_allotment_odds is deprecated. Use calculate_sebi_allotment_odds with PAN validation.")
