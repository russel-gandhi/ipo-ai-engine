def calculate_allotment_odds(category: str, lots_applied: int, subscription_multiple: float) -> dict:
    """
    Calculates the probability of getting at least one lot in an IPO.
    This uses a simplified proportionate lottery model per the project requirements.
    
    In a heavily oversubscribed scenario, the chance of getting a lot is roughly 1/S.
    SEBI rules prioritize giving at least 1 lot to as many applicants as possible.
    """
    
    if subscription_multiple <= 0:
        probability = 1.0
    elif subscription_multiple <= 1.0:
        probability = 1.0
    else:
        # Simplified math: roughly 1 / Subscription Multiple
        # In reality, retail ignores extra lots if oversubscribed, but to keep the analogy simple 
        # and respect the "roughly 1/S" requirement:
        probability = 1.0 / subscription_multiple

    prob_percentage = round(probability * 100, 2)
    
    # Fill in the Explain-Layer template context
    explain_template = (
        f"Based on {subscription_multiple}x subscription in the {category} category, "
        f"your estimated odds of getting at least one lot are roughly {prob_percentage}% — "
        f"think of it like {round(prob_percentage)} out of 100 raffle tickets like yours winning something. "
        f"(Note: This approximates the real SEBI lottery algorithm which has additional nuances.)"
    )

    return {
        "category": category,
        "lots_applied": lots_applied,
        "subscription_multiple": subscription_multiple,
        "probability_pct": prob_percentage,
        "explain_text": explain_template
    }
