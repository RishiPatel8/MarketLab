from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class InstrumentBase(BaseModel):
    exchange: str = Field(default="NSE", description="Exchange code: NSE or BSE")
    symbol: str = Field(..., description="Ticker symbol, e.g. GREENPOWER")
    company_name: str = Field(..., description="Full legal company name")
    instrument_type: str = Field(default="EQUITY")
    currency: str = Field(default="INR")
    sector: Optional[str] = None
    industry: Optional[str] = None
    isin: Optional[str] = None
    provider_identifier: Optional[str] = None

class InstrumentCreate(InstrumentBase):
    pass

class InstrumentResponse(InstrumentBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime

class InstrumentCandidate(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    match_reason: Optional[str] = None

class InstrumentResolutionResult(BaseModel):
    resolved: bool
    requires_clarification: bool = False
    instrument: Optional[InstrumentResponse] = None
    candidates: List[InstrumentCandidate] = []
    message: str
