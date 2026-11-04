from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Natural language research prompt")
    symbol: Optional[str] = Field(None, description="Optional explicit ticker symbol")
    exchange: Optional[str] = Field(default="NSE", description="NSE or BSE")
    investment_amount_inr: float = Field(default=50000.0, ge=100.0, description="Virtual capital allocated")
    horizon_days: Optional[int] = Field(default=180, description="Investment horizon in days")
    horizon_category: str = Field(default="medium_term", description="short_term (1-30d), medium_term (1-6mo), long_term (1yr+)")
    risk_tolerance: str = Field(default="moderate", description="conservative, moderate, aggressive")
    include_strategies: Optional[List[str]] = Field(default=None, description="Optional list of specific strategy keys to execute")
    include_technical: bool = Field(default=True)
    include_fundamental: bool = Field(default=True)
    include_rag: bool = Field(default=True)

class ResearchSpecification(BaseModel):
    research_id: str
    original_question: str
    symbol: str
    company_name: str
    exchange: str
    investment_amount_inr: float = 50000.0
    horizon_days: int
    horizon_category: str = "medium_term"
    risk_tolerance: str = "moderate"
    requested_strategies: List[str] = Field(default_factory=lambda: [
        "sma_crossover", "ema_crossover", "rsi_threshold", "macd_momentum",
        "bollinger_bands", "mean_reversion", "momentum_breakout", "fundamental_value"
    ])
    requested_analyses: List[str] = Field(default_factory=lambda: ["market_data", "financial_facts", "technical_indicators", "rag_evidence", "risk_factors", "decision_intelligence"])
    benchmark_symbol: str = "^NSEI"
    start_date: datetime
    end_date: datetime
    is_clarification_needed: bool = False
    clarification_prompt: Optional[str] = None

class ResearchRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    run_id: str
    status: str
    current_step: str
    progress_percentage: int
    message: Optional[str] = None
    resolved_instrument: Optional[Dict[str, Any]] = None
    clarification_candidates: Optional[List[Dict[str, Any]]] = None
    verification_status: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class ResearchRunSummary(BaseModel):
    id: str
    research_question: str
    status: str
    current_step: str
    progress_percentage: int
    resolved_instrument_id: Optional[str]
    verification_status: str
    created_at: datetime
    completed_at: Optional[datetime]
