from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class StrategyDefinitionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    strategy_key: str
    name: str
    category: str  # technical, fundamental, momentum, risk
    description: Optional[str] = None
    default_parameters: Dict[str, Any] = {}
    supported_timeframes: List[str] = ["1D"]
    version: str = "1.0.0"
    is_active: bool = True

class StrategyRunRequest(BaseModel):
    symbol: str
    exchange: str = "NSE"
    strategy_key: str
    parameters: Dict[str, Any] = {}
    initial_capital: float = 100000.0
    fee_pct: float = 0.001
    slippage_pct: float = 0.0005
    benchmark_symbol: str = "^NSEI"
    train_split: float = 0.7

class MultiStrategyRunRequest(BaseModel):
    symbol: str
    exchange: str = "NSE"
    strategy_keys: List[str] = Field(default_factory=lambda: [
        "sma_crossover", "ema_crossover", "rsi_threshold", "macd_momentum",
        "bollinger_bands", "mean_reversion", "momentum_breakout", "fundamental_value"
    ])
    initial_capital: float = 100000.0
    fee_pct: float = 0.001
    slippage_pct: float = 0.0005

class StrategySignal(BaseModel):
    strategy_key: str
    name: str
    category: str
    signal: str  # BUY, HOLD, SELL, NEUTRAL
    signal_strength: float = 0.5  # 0.0 to 1.0
    cagr: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    summary: str

class StrategyConsensusResult(BaseModel):
    total_strategies: int
    buy_signals: int
    hold_signals: int
    sell_signals: int
    consensus_rating: str  # BUY, HOLD, SELL, INSUFFICIENT_EVIDENCE
    consensus_percentage: float
    signals: List[StrategySignal]
