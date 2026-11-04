import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, Text
from app.db.session import Base

class ScenarioSimulation(Base):
    __tablename__ = "scenario_simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String(36), ForeignKey("virtual_portfolios.id"), nullable=True, index=True)
    research_run_id = Column(String(36), ForeignKey("research_runs.id"), nullable=True, index=True)
    scenario_name = Column(String(100), nullable=False)
    scenario_type = Column(String(50), default="market_shock")  # bull_rally, base_case, correction, severe_bear, sector_shock, rate_hike
    market_shock_pct = Column(Float, default=0.0)
    interest_rate_delta_bps = Column(Float, default=0.0)
    simulated_pnl = Column(Float, nullable=False, default=0.0)
    simulated_portfolio_value = Column(Float, nullable=False, default=0.0)
    estimated_max_loss = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    assumptions_json = Column(Text, nullable=True)  # JSON details of assumptions
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
