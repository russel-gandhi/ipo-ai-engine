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
    pan: Optional[str] = Field("ABCDE1234F", description="User's PAN for validation")
    category: Optional[str] = Field("Retail", description="Category: 'Retail', 'sHNI', 'bHNI', or 'QIB'")
    applied_amount: Optional[float] = Field(15000.0, description="Total amount applied in Rs.")
    ipo_data: Optional[IpoData] = Field(None, description="IPO quota and subscription data")

    # Direct calculator fields for interactive family PAN odds
    sub_retail: Optional[float] = Field(None, ge=0.0, description="Retail subscription multiple")
    retail_quota_pct: Optional[float] = Field(0.35, ge=0.0, le=1.0)
    issue_size_cr: Optional[float] = Field(None, gt=0)
    lot_size: Optional[int] = Field(None, gt=0)
    cutoff_price: Optional[float] = Field(None, gt=0)
    applied_lots_per_pan: Optional[int] = Field(1, ge=1)
    num_pans: Optional[int] = Field(1, ge=1, le=20)

class AllotmentResponse(BaseModel):
    category: str = "Retail"
    masked_pan: str = "⁕⁕⁕⁕⁕⁕1234F"
    probability_pct: float
    probability_at_least_one_lot: float = 0.0
    odds_per_pan: float = 0.0
    expected_lots: float = 0.0
    allotment_regime: str = "Proportionate Lottery"
    explain_text: str = ""
    guardrail: str = ""
    privacy_note: str = ""


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
    historical_gain_range: str = Field(..., description="Predicted gain range (e.g. '15-35%')")
    confidence_score: str = Field(..., description="Reliability indicator based on peer availability, walk-forward accuracy, and model agreement")
    real_peer_count: int = Field(0, description="Number of real scraped peers in this sector/size")
    walk_forward_accuracy_for_bucket: float = Field(0.0, description="The historical walk-forward accuracy for this specific bucket")
    model_agreement: bool = Field(True, description="True if XGBoost and Logistic baseline agree")
    disclaimer: str = Field("This output is based on historical pattern matching across similar past IPOs. It is not a prediction, recommendation, or investment advice.", description="Mandatory disclaimer")

# --- Peer Comparison schemas ---
class PeerComparisonRequest(BaseModel):
    issue_size: float = Field(..., gt=0, description="Total issue size in Rs. Cr.")
    sector: str = Field(..., description="Standardized sector of the company")
    
class PeerResult(BaseModel):
    company_name: str
    sector: str
    issue_size: float
    sub_overall: float = Field(0.0, description="Overall subscription multiple")
    gmp_at_close: str = Field("N/A", description="GMP at close")
    actual_listing_gain_pct: float
    retroactive_bucket_estimate: str
    retroactive_gain_range: str
    delta: float
    retroactive_confidence_score: str
    regime_warning: bool = Field(False, description="True for peers in the 2021 bull-market window")
    similarity_score: str = Field(..., description="How similar this peer is (e.g. 'Same Sector', 'Same Size')")
    
class PeerComparisonResponse(BaseModel):
    target_sector: str
    target_issue_size: float
    peer_hit_rate: str = Field(..., description="Model was within ±15% of actual listing gain in X out of Y similar past IPOs.")
    peers: list[PeerResult]
