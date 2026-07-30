from pydantic import BaseModel, Field
from typing import Optional

# --- Allotment schemas ---
class IpoData(BaseModel):
    retail_shares_quota: int = 0
    shni_shares_quota: int = 0
    bhni_shares_quota: int = 0
    qib_shares_quota: int = 0
    employee_shares_quota: int = 0
    qib_subscription_multiple: float = 0.0
    employee_subscription_multiple: float = 0.0
    retail_gross_applications: int = 0
    shni_gross_applications: int = 0
    bhni_gross_applications: int = 0
    min_lot_shares_retail: int = 1
    min_lot_shares_shni: int = 1
    min_lot_shares_bhni: int = 1

class AllotmentRequest(BaseModel):
    pan: str = Field(..., description="User's PAN for validation")
    category: str = Field(..., description="Category: 'Retail', 'sHNI', 'bHNI', or 'QIB'")
    applied_amount: float = Field(..., gt=0, description="Total amount applied in Rs.")
    ipo_data: IpoData = Field(..., description="IPO quota and subscription data")
    
class AllotmentResponse(BaseModel):
    category: str
    masked_pan: str
    probability_pct: float
    explain_text: str
    guardrail: str
    privacy_note: str


# --- Verdict schemas ---
class VerdictRequest(BaseModel):
    issue_size: float = Field(..., gt=0, description="Total issue size in Rs. Cr.")
    fresh_vs_ofs_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio of fresh issue to total issue size")
    sub_retail: float = Field(..., ge=0.0, description="Retail subscription multiple")
    sub_nii: float = Field(..., ge=0.0, description="NII subscription multiple")
    sub_qib: float = Field(..., ge=0.0, description="QIB subscription multiple")
    sub_overall: float = Field(..., ge=0.0, description="Overall subscription multiple")
    price_band: float = Field(..., gt=0, description="Upper price band per share in Rs.")
    sector: str = Field(..., description="Standardized sector of the company")
    gmp_trend: str = Field(..., description="Grey market premium trend: 'rising', 'flat', or 'falling'")
    is_sme: bool = Field(False, description="Is this an SME IPO?")
    anchor_allocation_pct: float = Field(0.0, description="Percentage allocated to anchor investors")
    relative_issue_size: float = Field(1.0, description="Size relative to sector average")
    gmp_trajectory: float = Field(0.0, description="Slope of GMP over time")
    market_regime_nifty_30d: float = Field(0.0, description="Trailing 30-day Nifty return")

class VerdictResponse(BaseModel):
    bucket_estimate: str = Field(..., description="'loss', 'flat', 'moderate', or 'high'")
    historical_gain_range: tuple[float, float] = Field(..., description="Predicted gain range based on confidence intervals")
    confidence_score: float = Field(..., description="Reliability score (0.0 to 1.0) based on peer availability and model agreement")
    real_peer_count: int = Field(0, description="Number of real scraped peers in this sector/size")
    total_peer_count: int = Field(0, description="Total peers including synthetics")
    disclaimer: str = Field(..., description="Mandatory disclaimer about Walk-Forward validation limits")

# --- Peer Comparison schemas ---
class PeerComparisonRequest(BaseModel):
    issue_size: float = Field(..., gt=0, description="Total issue size in Rs. Cr.")
    sector: str = Field(..., description="Standardized sector of the company")
    
class PeerResult(BaseModel):
    company_name: str
    sector: str
    issue_size: float
    actual_listing_gain_pct: float
    predicted_gain_pct: float
    similarity_score: str = Field(..., description="How similar this peer is (e.g. 'Same Sector', 'Same Size')")
    
class PeerComparisonResponse(BaseModel):
    target_sector: str
    target_issue_size: float
    peers: list[PeerResult]
