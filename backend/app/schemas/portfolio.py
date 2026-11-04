from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class VirtualPortfolioCreate(BaseModel):
    name: str = Field(default="Primary Virtual Portfolio", max_length=100)
    initial_capital: float = Field(default=100000.0, ge=1000.0)
    currency: str = "INR"
    portfolio_type: str = "paper_trade"  # backtest, paper_trade, what_if
    description: Optional[str] = None

class VirtualPositionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    portfolio_id: str
    instrument_id: str
    symbol: str
    exchange: str
    quantity: float
    average_entry_price: float
    current_price: float
    invested_amount: float
    current_value: float
    realized_pnl: float
    unrealized_pnl: float
    unrealized_pnl_pct: float = 0.0

class VirtualOrderCreate(BaseModel):
    symbol: str
    exchange: str = "NSE"
    order_type: str = "MARKET"  # MARKET, LIMIT
    side: str  # BUY, SELL
    quantity: float = Field(..., gt=0)
    requested_price: Optional[float] = None

class VirtualOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    portfolio_id: str
    symbol: str
    exchange: str
    order_type: str
    side: str
    quantity: float
    requested_price: Optional[float] = None
    executed_price: Optional[float] = None
    transaction_fee: float = 0.0
    slippage: float = 0.0
    status: str
    rejection_reason: Optional[str] = None
    executed_at: Optional[datetime] = None
    created_at: datetime

class VirtualPortfolioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    initial_capital: float
    cash_balance: float
    invested_capital: float = 0.0
    total_portfolio_value: float = 0.0
    total_unrealized_pnl: float = 0.0
    total_realized_pnl: float = 0.0
    total_return_pct: float = 0.0
    currency: str = "INR"
    portfolio_type: str
    status: str
    positions: List[VirtualPositionResponse] = []
    created_at: datetime

class ScenarioSimulationRequest(BaseModel):
    scenario_type: str = "market_shock"  # bull_rally, market_correction, severe_bear, rate_hike, sector_shock
    shock_pct: float = Field(..., description="e.g. -15.0 for 15% drop, +20.0 for 20% rally")
    sector_shock_pct: Optional[float] = 0.0
    notes: Optional[str] = None

class ScenarioSimulationResponse(BaseModel):
    id: str
    scenario_name: str
    scenario_type: str
    shock_pct: float
    baseline_portfolio_value: float
    simulated_portfolio_value: float
    simulated_pnl: float
    simulated_pnl_pct: float
    estimated_max_loss: float
    notes: Optional[str] = None
    created_at: datetime
