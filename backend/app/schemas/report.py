from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ResearchSourceCitation(BaseModel):
    source_title: str
    source_url_or_identifier: str
    publication_date: Optional[str] = None
    page_or_section: Optional[str] = None
    citation_text: str
    confidence_score: float = 1.0

class VerificationFindings(BaseModel):
    evidence_coverage_score: float = Field(default=1.0, ge=0.0, le=1.0)
    data_freshness_status: str = "fresh"  # fresh, acceptable, stale
    contradictions_detected: List[str] = []
    unsupported_claims_flagged: List[str] = []
    calculation_consistency: bool = True
    look_ahead_bias_audit: str = "passed"  # passed, warning, failed
    verification_passed: bool = True
    recommendations: List[str] = []

class ResearchReportResponse(BaseModel):
    report_id: str
    run_id: str
    instrument: Dict[str, Any]
    research_question: str
    sentiment_label: str  # bullish, neutral, bearish, inconclusive
    report_timestamp: datetime
    data_coverage: Dict[str, Any]
    market_data_provider: Optional[str] = "fixture"
    is_fixture: Optional[bool] = True
    latency_type: Optional[str] = "historical"
    embedding_provider: Optional[str] = "mock"
    is_mock_embedding: Optional[bool] = True
    llm_provider: Optional[str] = "mock"
    llm_model: Optional[str] = "mock"
    executive_summary: str
    business_financial_analysis: Optional[str] = None
    technical_analysis: Optional[str] = None
    financial_metrics: Dict[str, Any] = {}
    technical_metrics: Dict[str, Any] = {}
    positive_evidence: List[str] = []
    negative_evidence: List[str] = []
    key_risks: List[str] = []
    sources: List[ResearchSourceCitation] = []
    verification: VerificationFindings
    limitations: List[str] = []
    # Decision Intelligence extensions
    decision_rating: str = "INSUFFICIENT_EVIDENCE"  # BUY, HOLD, SELL, INSUFFICIENT_EVIDENCE
    entry_price_min: Optional[float] = None
    entry_price_max: Optional[float] = None
    fair_value_min: Optional[float] = None
    fair_value_max: Optional[float] = None
    target_bull: Optional[float] = None
    target_base: Optional[float] = None
    target_bear: Optional[float] = None
    stop_loss_price: Optional[float] = None
    horizon_type: Optional[str] = "medium_term"
    strategy_consensus: Optional[Dict[str, Any]] = None
    scenario_projections: Optional[List[Dict[str, Any]]] = None
    sebi_notice: str = (
        "SEBI Non-Advisory Notice: MarketLab AI is a non-brokerage quantitative research and virtual simulation environment. "
        "Outputs are for research support and do not constitute registered investment advice."
    )
    report_markdown: str
    is_completed_with_limitations: bool = False
