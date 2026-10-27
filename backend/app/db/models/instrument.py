import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Index
from app.db.session import Base

class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exchange = Column(String(20), nullable=False, default="NSE", index=True)  # NSE, BSE
    symbol = Column(String(50), nullable=False, index=True)  # GREENPOWER, RELIANCE, TATAMOTORS
    company_name = Column(String(255), nullable=False, index=True)
    instrument_type = Column(String(50), default="EQUITY")
    currency = Column(String(10), default="INR")
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    isin = Column(String(20), nullable=True)
    provider_identifier = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_exchange_symbol", "exchange", "symbol", unique=True),
    )
