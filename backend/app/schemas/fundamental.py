from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class DCFValuationResult(BaseModel):
    fair_value_per_share: float
    current_market_price: float
    margin_of_safety_pct: float
    projected_growth_rate: float
    terminal_growth_rate: float
    wacc: float
    valuation_status: str  # UNDERVALUED, FAIRLY_VALUED, OVERVALUED
    sensitivity_matrix: Dict[str, Dict[str, float]] = {}  # WACC vs Terminal Growth rates

class DuPontAnalysisResult(BaseModel):
    roe: float
    net_profit_margin: float
    asset_turnover: float
    equity_multiplier: float
    interpretation: str

class PeerComparisonItem(BaseModel):
    symbol: str
    company_name: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roce: Optional[float] = None
    market_cap_tier: str = "Large Cap"
    debt_to_equity: Optional[float] = None

class FundamentalAnalysisResult(BaseModel):
    symbol: str
    company_name: str
    fiscal_period: str
    revenue_cr: Optional[float] = None
    operating_profit_cr: Optional[float] = None
    net_profit_cr: Optional[float] = None
    eps: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    free_cash_flow_cr: Optional[float] = None
    dcf_valuation: Optional[DCFValuationResult] = None
    dupont: Optional[DuPontAnalysisResult] = None
    peers: List[PeerComparisonItem] = []
    fundamental_score: float = Field(default=5.0, ge=0.0, le=10.0)
    summary: str
