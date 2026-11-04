from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class PriceTargetScenario(BaseModel):
    scenario: str  # BULL, BASE, BEAR
    probability: float  # e.g., 0.25, 0.50, 0.25
    target_price: float
    expected_return_pct: float
    rationale: str

class DecisionReportResponse(BaseModel):
    decision_rating: str  # BUY, HOLD, SELL, INSUFFICIENT_EVIDENCE
    recommendation_summary: str
    current_price: float
    price_timestamp: datetime
    entry_range_min: float
    entry_range_max: float
    fair_value_min: float
    fair_value_max: float
    stop_loss_price: float
    risk_reward_ratio: float
    horizon_type: str  # short_term, medium_term, long_term
    investment_amount_inr: float
    recommended_position_quantity: int
    scenarios: List[PriceTargetScenario] = []
    strategy_consensus: Dict[str, Any] = {}
    evidence_coverage_score: float = 1.0
    confidence_level: str = "HIGH"  # HIGH, MODERATE, LOW, INSUFFICIENT
    sebi_non_advisory_notice: str = (
        "SEBI Non-Advisory Notice: MarketLab AI is a decision-support, research, and virtual simulation system. "
        "It does not provide registered financial advice, broker execution, or guaranteed returns."
    )
