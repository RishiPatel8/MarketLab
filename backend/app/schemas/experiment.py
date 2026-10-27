from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ExperimentCreate(BaseModel):
    instrument_id: Optional[str] = None
    symbol: Optional[str] = "GREENPOWER"
    exchange: Optional[str] = "NSE"
    strategy_type: str = Field(default="sma_crossover", description="Strategy identifier")
    parameters: Dict[str, Any] = Field(default_factory=lambda: {"fast_period": 20, "slow_period": 50})
    initial_capital: float = Field(default=100000.0, gt=0)
    transaction_fee_pct: float = Field(default=0.001, ge=0.0, description="0.1% transaction cost")
    slippage_pct: float = Field(default=0.0005, ge=0.0, description="0.05% execution slippage")
    benchmark_symbol: str = Field(default="^NSEI", description="Benchmark symbol")
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ExperimentMetricResponse(BaseModel):
    cagr: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: Optional[float] = None
    annualized_volatility: float
    win_rate: float
    profit_factor: float
    total_trades: int
    benchmark_cagr: Optional[float] = None
    benchmark_max_drawdown: Optional[float] = None
    equity_curve: List[Dict[str, Any]] = []
    trades: List[Dict[str, Any]] = []

class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    instrument_id: str
    symbol: str
    strategy_type: str
    strategy_configuration: Dict[str, Any]
    cost_assumptions: Dict[str, Any]
    status: str
    engine_version: str
    created_at: datetime
    metrics: Optional[ExperimentMetricResponse] = None
