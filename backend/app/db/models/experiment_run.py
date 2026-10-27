import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Integer, Index
from app.db.session import Base

class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    research_run_id = Column(String(36), ForeignKey("research_runs.id"), nullable=True, index=True)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False, index=True)
    strategy_type = Column(String(50), nullable=False, default="sma_crossover")
    strategy_configuration = Column(Text, nullable=False)  # JSON
    dataset_reference = Column(String(255), nullable=False)
    benchmark_symbol = Column(String(50), default="^NSEI")
    cost_assumptions = Column(Text, nullable=False)  # JSON {fee_pct, slippage_pct}
    status = Column(String(50), default="completed")  # queued, running, completed, failed
    engine_version = Column(String(50), default="1.0.0")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class ExperimentMetric(Base):
    __tablename__ = "experiment_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_run_id = Column(String(36), ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    cagr = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=False)
    sortino_ratio = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    calmar_ratio = Column(Float, nullable=True)
    annualized_volatility = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    total_trades = Column(Integer, nullable=False)
    benchmark_cagr = Column(Float, nullable=True)
    benchmark_max_drawdown = Column(Float, nullable=True)
    out_of_sample_metrics = Column(Text, nullable=True)  # JSON
    equity_curve_json = Column(Text, nullable=True)  # JSON series for charting
    trades_json = Column(Text, nullable=True)  # JSON trade logs
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
