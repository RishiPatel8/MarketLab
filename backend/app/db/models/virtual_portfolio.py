import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, Text
from app.db.session import Base

class VirtualPortfolio(Base):
    __tablename__ = "virtual_portfolios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String(100), nullable=False, default="Primary Virtual Portfolio")
    initial_capital = Column(Float, nullable=False, default=100000.0)
    cash_balance = Column(Float, nullable=False, default=100000.0)
    currency = Column(String(10), default="INR")
    portfolio_type = Column(String(50), default="paper_trade")  # backtest, paper_trade, what_if
    status = Column(String(30), default="active")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class VirtualPosition(Base):
    __tablename__ = "virtual_positions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String(36), ForeignKey("virtual_portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(20), default="NSE")
    quantity = Column(Float, nullable=False, default=0.0)
    average_entry_price = Column(Float, nullable=False, default=0.0)
    current_price = Column(Float, nullable=False, default=0.0)
    invested_amount = Column(Float, nullable=False, default=0.0)
    current_value = Column(Float, nullable=False, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_port_inst", "portfolio_id", "instrument_id", unique=True),
    )


class VirtualOrder(Base):
    __tablename__ = "virtual_orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String(36), ForeignKey("virtual_portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False)
    exchange = Column(String(20), default="NSE")
    order_type = Column(String(20), default="MARKET")  # MARKET, LIMIT
    side = Column(String(10), nullable=False)  # BUY, SELL
    quantity = Column(Float, nullable=False)
    requested_price = Column(Float, nullable=True)
    executed_price = Column(Float, nullable=True)
    transaction_fee = Column(Float, default=0.0)
    slippage = Column(Float, default=0.0)
    status = Column(String(20), default="FILLED")  # PENDING, FILLED, REJECTED, CANCELLED
    rejection_reason = Column(String(255), nullable=True)
    executed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
