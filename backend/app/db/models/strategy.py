import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime
from app.db.session import Base

class StrategyDefinition(Base):
    __tablename__ = "strategy_definitions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_key = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, default="technical")  # technical, fundamental, momentum, risk
    description = Column(Text, nullable=True)
    default_parameters_json = Column(Text, nullable=False, default="{}")
    supported_timeframes_json = Column(Text, nullable=False, default='["1D"]')
    version = Column(String(20), default="1.0.0")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
