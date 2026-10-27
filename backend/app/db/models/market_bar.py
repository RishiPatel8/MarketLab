import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index, Boolean
from app.db.session import Base

class MarketBar(Base):
    __tablename__ = "market_bars"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(Float, nullable=False)
    provider = Column(String(50), default="fixture")
    is_validated = Column(Boolean, default=True)
    validation_notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_inst_timestamp", "instrument_id", "timestamp", unique=True),
    )
