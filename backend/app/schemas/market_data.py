from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class MarketBarSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    timestamp: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    adjusted_close: Optional[float] = None
    volume: float = Field(..., ge=0)
    provider: str = "fixture"

class MarketDataValidationResult(BaseModel):
    is_valid: bool
    total_bars: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    anomalies_detected: int = 0
    issues: List[str] = []
    coverage_percentage: float = 100.0
    provider_attribution: str = "fixture"
    latency_type: str = "end_of_day"

class MarketDataResponse(BaseModel):
    instrument_id: str
    symbol: str
    exchange: str
    validation: MarketDataValidationResult
    bars: List[MarketBarSchema]
