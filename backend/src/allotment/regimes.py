from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

@dataclass
class AllotmentRule:
    rule_id: str
    investor_category: str
    board_type: str
    issue_type: str
    effective_from: str
    effective_until: Optional[str]
    
    minimum_application_rule: str
    allocation_method: str
    oversubscription_method: str
    minimum_allotment_method: str
    residual_allocation_method: str
    
    source_type: str = "SEBI_REGULATION"
    authority_level: int = 1
    
    required_inputs_for_probability: List[str] = field(default_factory=list)
    
    regulation_reference: str = ""
    source_url: str = ""

REGIME_RULES: Dict[str, Dict[str, AllotmentRule]] = {
    "MAINBOARD_PRE_2022": {
        "RETAIL": AllotmentRule(
            rule_id="MAINBOARD_PRE22_RETAIL",
            investor_category="Retail",
            board_type="Mainboard",
            issue_type="Book-Built",
            effective_from="2018-09-11",
            effective_until="2022-03-31",
            minimum_application_rule="1 Market Lot (up to ₹2 Lakhs)",
            allocation_method="MINIMUM_ALLOTMENT_THEN_LOTTERY",
            oversubscription_method="DRAW_OF_LOTS",
            minimum_allotment_method="1 Minimum Market Lot",
            residual_allocation_method="Spillover to NII/QIB if undersubscribed",
            source_type="SEBI_REGULATION",
            authority_level=1,
            required_inputs_for_probability=["category_quota_shares", "minimum_allotment_shares", "valid_application_count"],
            regulation_reference="SEBI (ICDR) Regulations 2018, Schedule XIII, Part A",
            source_url="https://www.sebi.gov.in/legal/regulations/sep-2018/securities-and-exchange-board-of-india-issue-of-capital-and-disclosure-requirements-regulations-2018_40388.html"
        ),
        "NII": AllotmentRule(
            rule_id="MAINBOARD_PRE22_NII",
            investor_category="NII",
            board_type="Mainboard",
            issue_type="Book-Built",
            effective_from="2018-09-11",
            effective_until="2022-03-31",
            minimum_application_rule="> ₹2 Lakhs",
            allocation_method="PROPORTIONATE",
            oversubscription_method="PROPORTIONATE",
            minimum_allotment_method="Proportionate to shares bid",
            residual_allocation_method="Spillover to Retail/QIB if undersubscribed",
            source_type="SEBI_REGULATION",
            authority_level=1,
            required_inputs_for_probability=["shares_bid", "shares_offered"],
            regulation_reference="SEBI (ICDR) Regulations 2018, Schedule XIII, Part A",
            source_url="https://www.sebi.gov.in/legal/regulations/sep-2018/securities-and-exchange-board-of-india-issue-of-capital-and-disclosure-requirements-regulations-2018_40388.html"
        )
    },
    "MAINBOARD_POST_2022": {
        "RETAIL": AllotmentRule(
            rule_id="MAINBOARD_POST22_RETAIL",
            investor_category="Retail",
            board_type="Mainboard",
            issue_type="Book-Built",
            effective_from="2022-04-01",
            effective_until=None,
            minimum_application_rule="1 Market Lot (up to ₹2 Lakhs)",
            allocation_method="MINIMUM_ALLOTMENT_THEN_LOTTERY",
            oversubscription_method="DRAW_OF_LOTS",
            minimum_allotment_method="1 Minimum Market Lot subject to availability",
            residual_allocation_method="Spillover to NII/QIB if undersubscribed",
            source_type="SEBI_REGULATION",
            authority_level=1,
            required_inputs_for_probability=["category_quota_shares", "minimum_allotment_shares", "valid_application_count"],
            regulation_reference="SEBI (ICDR) Regulations 2018, Schedule XIII, Part A",
            source_url="https://www.sebi.gov.in/legal/regulations/sep-2018/securities-and-exchange-board-of-india-issue-of-capital-and-disclosure-requirements-regulations-2018_40388.html"
        ),
        "sNII": AllotmentRule(
            rule_id="MAINBOARD_POST22_SNII",
            investor_category="sNII",
            board_type="Mainboard",
            issue_type="Book-Built",
            effective_from="2022-04-01",
            effective_until=None,
            minimum_application_rule="₹2,00,001 to ₹10,00,000 (1/3 of NII Quota)",
            allocation_method="MINIMUM_ALLOTMENT_THEN_LOTTERY",
            oversubscription_method="DRAW_OF_LOTS_FOR_MIN_LOT",
            minimum_allotment_method="Minimum allotment size subject to availability + draw of lots where necessary to identify successful applicants + proportionate balance allocation where applicable",
            residual_allocation_method="Unallotted shares spillover to bNII",
            source_type="SEBI_AMENDMENT",
            authority_level=1,
            required_inputs_for_probability=["category_quota_shares", "minimum_allotment_shares", "valid_application_count"],
            regulation_reference="SEBI (ICDR) (Amendment) Regulations 2021, Regulation 49(2)",
            source_url="https://www.sebi.gov.in/legal/regulations/jan-2022/securities-and-exchange-board-of-india-issue-of-capital-and-disclosure-requirements-amendment-regulations-2021_55325.html"
        ),
        "bNII": AllotmentRule(
            rule_id="MAINBOARD_POST22_BNII",
            investor_category="bNII",
            board_type="Mainboard",
            issue_type="Book-Built",
            effective_from="2022-04-01",
            effective_until=None,
            minimum_application_rule="> ₹10,00,000 (2/3 of NII Quota)",
            allocation_method="MINIMUM_ALLOTMENT_THEN_PROPORTIONATE",
            oversubscription_method="DRAW_OF_LOTS_THEN_PROPORTIONATE",
            minimum_allotment_method="Minimum allotment lot to successful applicants + proportionate allocation of residual shares",
            residual_allocation_method="Unallotted shares spillover to sNII",
            source_type="SEBI_AMENDMENT",
            authority_level=1,
            required_inputs_for_probability=["category_quota_shares", "minimum_allotment_shares", "valid_application_count", "total_shares_bid"],
            regulation_reference="SEBI (ICDR) (Amendment) Regulations 2021, Regulation 49(2)",
            source_url="https://www.sebi.gov.in/legal/regulations/jan-2022/securities-and-exchange-board-of-india-issue-of-capital-and-disclosure-requirements-amendment-regulations-2021_55325.html"
        ),
        "QIB": AllotmentRule(
            rule_id="MAINBOARD_POST22_QIB",
            investor_category="QIB",
            board_type="Mainboard",
            issue_type="Book-Built",
            effective_from="2022-04-01",
            effective_until=None,
            minimum_application_rule="1 Market Lot",
            allocation_method="PROPORTIONATE",
            oversubscription_method="PROPORTIONATE",
            minimum_allotment_method="Proportionate to shares bid",
            residual_allocation_method="Spillover to NII/Retail if allowed by RHP",
            source_type="SEBI_REGULATION",
            authority_level=1,
            required_inputs_for_probability=["shares_bid", "shares_offered"],
            regulation_reference="SEBI (ICDR) Regulations 2018, Regulation 32",
            source_url="https://www.sebi.gov.in/legal/regulations/sep-2018/securities-and-exchange-board-of-india-issue-of-capital-and-disclosure-requirements-regulations-2018_40388.html"
        )
    },
    "SME_OLD_FRAMEWORK": {
        "RETAIL": AllotmentRule(
            rule_id="SME_OLD_RETAIL",
            investor_category="Retail",
            board_type="SME",
            issue_type="Book-Built / Fixed-Price",
            effective_from="2018-09-11",
            effective_until="2024-12-31",
            minimum_application_rule="1 Market Lot (Min ₹1 Lakh)",
            allocation_method="MINIMUM_ALLOTMENT_THEN_LOTTERY",
            oversubscription_method="DRAW_OF_LOTS",
            minimum_allotment_method="1 Market Lot",
            residual_allocation_method="Spillover to Non-Retail",
            source_type="SEBI_REGULATION",
            authority_level=2,
            required_inputs_for_probability=["category_quota_shares", "minimum_allotment_shares", "valid_application_count"],
            regulation_reference="SEBI (ICDR) Regulations 2018, Chapter IX, Regulation 253",
            source_url="https://www.sebi.gov.in/legal/regulations/sep-2018/securities-and-exchange-board-of-india-issue-of-capital-and-disclosure-requirements-regulations-2018_40388.html"
        ),
        "NII": AllotmentRule(
            rule_id="SME_OLD_NII",
            investor_category="NII",
            board_type="SME",
            issue_type="Book-Built / Fixed-Price",
            effective_from="2018-09-11",
            effective_until="2024-12-31",
            minimum_application_rule="> ₹1 Lakh",
            allocation_method="PROPORTIONATE",
            oversubscription_method="PROPORTIONATE",
            minimum_allotment_method="Proportionate subject to market lot rounding",
            residual_allocation_method="Spillover to Retail",
            source_type="SEBI_REGULATION",
            authority_level=2,
            required_inputs_for_probability=["shares_bid", "shares_offered"],
            regulation_reference="SEBI (ICDR) Regulations 2018, Chapter IX, Regulation 253",
            source_url="https://www.sebi.gov.in/legal/regulations/sep-2018/securities-and-exchange-board-of-india-issue-of-capital-and-disclosure-requirements-regulations-2018_40388.html"
        )
    },
    "SME_2025_FRAMEWORK": {
        "RETAIL": AllotmentRule(
            rule_id="SME_2025_RETAIL",
            investor_category="Retail",
            board_type="SME",
            issue_type="Book-Built / Fixed-Price",
            effective_from="2025-01-01",
            effective_until=None,
            minimum_application_rule="2 Market Lots (Min > ₹2 Lakhs)",
            allocation_method="MINIMUM_ALLOTMENT_THEN_LOTTERY",
            oversubscription_method="DRAW_OF_LOTS",
            minimum_allotment_method="Minimum 2 Market Lots",
            residual_allocation_method="Spillover to Non-Retail",
            source_type="SEBI_CIRCULAR",
            authority_level=3,
            required_inputs_for_probability=["category_quota_shares", "minimum_allotment_shares", "valid_application_count"],
            regulation_reference="SEBI (ICDR) (SME Amendment) Regulations 2024; BSE Circular 20241220-12",
            source_url="https://www.sebi.gov.in"
        ),
        "NII": AllotmentRule(
            rule_id="SME_2025_NII",
            investor_category="NII",
            board_type="SME",
            issue_type="Book-Built / Fixed-Price",
            effective_from="2025-01-01",
            effective_until=None,
            minimum_application_rule="As per RHP",
            allocation_method="PROPORTIONATE",
            oversubscription_method="PROPORTIONATE",
            minimum_allotment_method="Proportionate subject to market lot rounding",
            residual_allocation_method="Spillover to Retail",
            source_type="SEBI_CIRCULAR",
            authority_level=3,
            required_inputs_for_probability=["shares_bid", "shares_offered"],
            regulation_reference="SEBI (ICDR) (SME Amendment) Regulations 2024; BSE Circular 20241220-12",
            source_url="https://www.sebi.gov.in"
        )
    }
}


def resolve_ipo_regime_id(ipo_data: Dict[str, Any]) -> str:
    """
    Resolves the regime ID for an IPO dynamically based on its board type,
    issue dates, and regulatory operative effective dates.
    """
    is_sme = ipo_data.get("is_sme", False) or "SME" in str(ipo_data.get("exchange", "")).upper()
    open_date_str = ipo_data.get("open_date") or ipo_data.get("close_date")
    
    open_date = None
    if open_date_str:
        try:
            open_date = datetime.strptime(open_date_str[:10], "%Y-%m-%d").date()
        except Exception:
            open_date = None
            
    if is_sme:
        # Legally operative transition date for SME 2025 Framework
        if open_date and open_date >= datetime.strptime("2025-01-01", "%Y-%m-%d").date():
            return "SME_2025_FRAMEWORK"
        return "SME_OLD_FRAMEWORK"
    else:
        # Legally operative transition date for SEBI ICDR 2021 NII Amendment
        if open_date and open_date < datetime.strptime("2022-04-01", "%Y-%m-%d").date():
            return "MAINBOARD_PRE_2022"
        return "MAINBOARD_POST_2022"


def get_applicable_rule(ipo_data: Dict[str, Any], category: str) -> AllotmentRule:
    """
    Retrieves the exact versioned AllotmentRule for an IPO and investor category.
    """
    regime_id = resolve_ipo_regime_id(ipo_data)
    regime_rules = REGIME_RULES.get(regime_id, REGIME_RULES["MAINBOARD_POST_2022"])
    
    cat_upper = category.upper()
    if "RETAIL" in cat_upper or "INDIVIDUAL" in cat_upper:
        target_cat = "RETAIL"
    elif "SNII" in cat_upper or "SHNI" in cat_upper:
        target_cat = "sNII" if "sNII" in regime_rules else "NII"
    elif "BNII" in cat_upper or "BHNI" in cat_upper:
        target_cat = "bNII" if "bNII" in regime_rules else "NII"
    elif "QIB" in cat_upper:
        target_cat = "QIB"
    else:
        target_cat = "RETAIL"
        
    rule = regime_rules.get(target_cat)
    if not rule:
        rule = list(regime_rules.values())[0]
        
    return rule
