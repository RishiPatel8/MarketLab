from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Natural language research prompt")
    symbol: Optional[str] = Field(None, description="Optional explicit ticker symbol")
    exchange: Optional[str] = Field(default="NSE", description="NSE or BSE")
    horizon_days: Optional[int] = Field(default=180, description="Investment horizon in days")
    include_technical: bool = Field(default=True)
    include_fundamental: bool = Field(default=True)
    include_rag: bool = Field(default=True)

class ResearchSpecification(BaseModel):
    research_id: str
    original_question: str
    symbol: str
    company_name: str
    exchange: str
    horizon_days: int
    requested_analyses: List[str] = Field(default_factory=lambda: ["market_data", "financial_facts", "technical_indicators", "rag_evidence", "risk_factors"])
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
