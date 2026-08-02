from backend.src.allotment.engine import calculate_allotment_engine, validate_pan, mask_pan

def calculate_sebi_allotment_odds(
    pan: str,
    category: str,
    applied_amount: float,
    ipo_data: dict
) -> dict:
    """
    Legacy wrapper routing through centralized regulatory allotment engine.
    """
    payload = {
        "pan": pan,
        "category": category,
        "applied_amount": applied_amount,
        "ipo_data": ipo_data
    }
    response = calculate_allotment_engine(payload)
    return {
        "category": response.category,
        "masked_pan": response.masked_pan,
        "probability_pct": response.probability_pct or 0.0,
        "explain_text": response.explain_text,
        "guardrail": response.guardrail,
        "privacy_note": response.privacy_note,
        "audit_trace": response.audit_trace.model_dump()
    }

def calculate_allotment_odds(*args, **kwargs):
    raise DeprecationWarning("calculate_allotment_odds is deprecated. Use calculate_sebi_allotment_odds or calculate_allotment_engine.")
