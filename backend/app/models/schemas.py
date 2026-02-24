from typing import List

from pydantic import BaseModel, Field


class FraudEvaluationRequest(BaseModel):
    transaction_id: str = Field(..., examples=["TXN-22044"])
    supplier_id: str = Field(..., examples=["SUP-108"])
    buyer_id: str = Field(..., examples=["BUY-208"])
    invoice_amount: float = Field(..., ge=0)
    invoice_currency: str = "USD"
    invoice_count_last_30d: int = Field(..., ge=0)
    shipment_distance_km: float = Field(..., ge=0)
    shipment_delay_hours: float = Field(..., ge=0)
    payment_term_days: int = Field(..., ge=0)
    contract_value: float = Field(..., ge=0)
    country_risk_index: float = Field(..., ge=0, le=1)
    sanctions_hit: bool = False
    beneficial_owner_mismatch: bool = False
    split_invoice_pattern: bool = False
    tier_level: int = Field(..., ge=1, le=6)


class ScoreBreakdown(BaseModel):
    anomaly_score: float
    rule_score: float
    network_score: float


class FraudEvaluationResponse(BaseModel):
    transaction_id: str
    risk_score: float
    risk_band: str
    score_breakdown: ScoreBreakdown
    reason_codes: List[str]
    recommendation: str
