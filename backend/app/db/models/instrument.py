import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Index
from app.db.session import Base

class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exchange = Column(String(30), nullable=False, default="NSE", index=True)  # NSE, BSE, NSE,BSE, AMFI
    symbol = Column(String(50), nullable=False, index=True)  # Primary trading ticker or identifier
    canonical_name = Column(String(255), nullable=True, index=True)
    display_name = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=False, index=True)
    instrument_type = Column(String(50), default="EQUITY", index=True)  # EQUITY, SME_EQUITY, ETF, MUTUAL_FUND, INDEX
    currency = Column(String(10), default="INR")
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    isin = Column(String(20), nullable=True, index=True)
    
    # Dual-listing and exchange-specific identifiers
    nse_symbol = Column(String(50), nullable=True, index=True)
    bse_code = Column(String(20), nullable=True, index=True)
    bse_symbol = Column(String(50), nullable=True, index=True)
    
    # Mutual fund scheme details
    scheme_code = Column(String(30), nullable=True, index=True)
    amc_or_issuer = Column(String(255), nullable=True, index=True)
    scheme_category = Column(String(100), nullable=True)
    plan_type = Column(String(30), nullable=True)  # Direct / Regular
    option_type = Column(String(30), nullable=True)  # Growth / IDCW
    latest_nav = Column(Float, nullable=True)
    latest_nav_date = Column(DateTime, nullable=True)

    # Status, provenance, and data availability
    status = Column(String(20), default="ACTIVE", index=True)  # ACTIVE, SUSPENDED, DELISTED
    source_provider = Column(String(50), default="NSE")  # NSE, BSE, AMFI, SEED
    source_record_identifier = Column(String(100), nullable=True)
    data_availability = Column(String(50), default="SUPPORTED", index=True)  # SUPPORTED, UNAVAILABLE, NAV_ONLY
    aliases = Column(String(500), nullable=True)
    
    last_sync_timestamp = Column(DateTime, nullable=True)
    last_verified_timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_exchange_symbol", "exchange", "symbol"),
        Index("idx_type_exchange", "instrument_type", "exchange"),
    )
