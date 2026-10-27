import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, Boolean
from app.db.session import Base

class FinancialFact(Base):
    __tablename__ = "financial_facts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False, index=True)
    period = Column(String(50), nullable=False)  # e.g., FY2024, Q3-FY2025
    report_date = Column(DateTime, nullable=False)
    revenue = Column(Float, nullable=True)  # in INR Crores
    operating_profit = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=True)
    eps = Column(Float, nullable=True)
    total_debt = Column(Float, nullable=True)
    equity = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)  # Percentage
    roce = Column(Float, nullable=True)  # Percentage
    operating_margin = Column(Float, nullable=True)  # Percentage
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    source_url_or_id = Column(String(255), nullable=True)
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_inst_period", "instrument_id", "period", unique=True),
    )
