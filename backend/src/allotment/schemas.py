from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SourceMetadata(BaseModel):
    source: str = Field(..., description="Authoritative source name")
    source_type: str = Field("SEBI_REGULATION", description="Source classification: SEBI_REGULATION, SEBI_AMENDMENT, SEBI_CIRCULAR, EXCHANGE_CIRCULAR, OFFER_DOCUMENT, BASIS_OF_ALLOTMENT")
    authority_level: int = Field(1, description="Authority priority level (1=Highest to 6=Lowest)")
    source_url: Optional[str] = Field(None, description="Direct URL to official document or filing")
    retrieved_at: Optional[str] = Field(None, description="ISO timestamp when data was fetched")
    effective_at: Optional[str] = Field(None, description="ISO date when regulation became effective")
    is_final: bool = Field(True, description="Whether this data point is final")
    confidence: str = Field("HIGH", description="Confidence level: HIGH, MEDIUM, LOW, RULE_BASED")

class CategorySubscription(BaseModel):
    shares_offered: Optional[int] = None
    shares_bid: Optional[int] = None
    applications: Optional[int] = None
    share_subscription_multiple: Optional[float] = None
    application_oversubscription_multiple: Optional[float] = None
    timestamp: Optional[str] = None
    source: Optional[str] = None
    is_final: bool = False

class BasisOfAllotmentData(BaseModel):
    is_published: bool = False
    source_url: Optional[str] = None
    published_at: Optional[str] = None
    valid_applications_by_category: Dict[str, int] = {}
    allotment_ratio_by_category: Dict[str, float] = {}
    category_details: Dict[str, Any] = {}

class AllotmentAuditTrace(BaseModel):
    regime_id: str
    rule_id: str
    rule_version: str
    board_type: str
    issue_type: str
    effective_period: str
    category: str
    
    # Source classification
    source_type: str = "SEBI_REGULATION"
    authority_level: int = 1
    
    # State flags
    rule_known: bool = True
    calculation_data_complete: bool = False
    required_inputs: List[str] = []
    available_inputs: List[str] = []
    missing_inputs: List[str] = []
    
    # Inputs used
    inputs_used: Dict[str, Any] = {}
    category_quota_shares: Optional[int] = None
    minimum_allotment_shares: Optional[int] = None
    minimum_allotment_lots: Optional[int] = None
    
    # Multiples
    share_subscription_multiple: Optional[float] = None
    application_oversubscription_multiple: Optional[float] = None
    
    # Steps and Calculation
    allocation_method: str
    calculation_steps: List[str] = []
    
    # Odds & Expected Allotment (Strictly null if calculation_data_complete is False)
    exact_probability: Optional[float] = None
    estimated_probability: Optional[float] = None
    status: str # "EXACT", "INSUFFICIENT_APPLICATION_DATA", "PROPORTIONATE", "FINAL_BASIS_OF_ALLOTMENT"
    
    expected_allotment_shares: Optional[float] = None
    expected_allotment_lots: Optional[float] = None
    
    # Explanations and Disclaimers
    assumptions: List[str] = []
    limitations: List[str] = []
    regulation_reference: str
    source_url: Optional[str] = None
    confidence: str = "HIGH"

class EnrichedAllotmentResponse(BaseModel):
    category: str
    masked_pan: str
    
    rule_known: bool
    calculation_data_complete: bool
    calculation_status: str 
    status_label: str # e.g. "Exact Allotment Odds Unavailable"
    
    probability_pct: Optional[float] = None
    estimated_probability_pct: Optional[float] = None
    probability_at_least_one_lot: Optional[float] = None  # Estimated probability of >= 1 lot across family PANs
    
    share_subscription_multiple: Optional[float] = None
    application_oversubscription_multiple: Optional[float] = None
    
    expected_lots: Optional[float] = None
    expected_shares: Optional[float] = None
    expected_value: Optional[float] = None
    
    allotment_regime: str
    explain_text: str
    guardrail: str
    privacy_note: str = "PAN data lives strictly in volatile memory and is never written to persistent storage."
    
    audit_trace: AllotmentAuditTrace
