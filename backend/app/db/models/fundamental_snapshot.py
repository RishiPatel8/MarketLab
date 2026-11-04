import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, Boolean, Text
from app.db.session import Base

class FundamentalSnapshot(Base):
    __tablename__ = "fundamental_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False, index=True)
    fiscal_period = Column(String(50), nullable=False)  # e.g., FY2024, FY2025, TTM
    report_date = Column(DateTime, nullable=False)
    revenue = Column(Float, nullable=True)  # in INR Crores
    operating_profit = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=True)
    eps = Column(Float, nullable=True)
    total_debt = Column(Float, nullable=True)
    equity = Column(Float, nullable=True)
    free_cash_flow = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)  # %
    roce = Column(Float, nullable=True)  # %
    operating_margin = Column(Float, nullable=True)  # %
    net_margin = Column(Float, nullable=True)  # %
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    ev_ebitda = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    dcf_fair_value = Column(Float, nullable=True)
    dcf_assumptions_json = Column(Text, nullable=True)  # WACC, terminal growth, discount rate
    dupont_analysis_json = Column(Text, nullable=True)  # Margin, Turnover, Leverage
    peer_comparisons_json = Column(Text, nullable=True)  # JSON array of peer metrics
    data_source = Column(String(100), default="regulatory_filing")
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_fund_inst_period", "instrument_id", "fiscal_period", unique=True),
    )
