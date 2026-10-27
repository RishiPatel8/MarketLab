from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.market_bar import MarketBar
from app.schemas.market_data import MarketBarSchema

class MarketDataRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_bars_for_instrument(
        self,
        instrument_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MarketBar]:
        query = self.db.query(MarketBar).filter(MarketBar.instrument_id == instrument_id)
        if start_date:
            query = query.filter(MarketBar.timestamp >= start_date)
        if end_date:
            query = query.filter(MarketBar.timestamp <= end_date)
        return query.order_by(MarketBar.timestamp.asc()).all()

    def save_bars(self, instrument_id: str, bars: List[MarketBarSchema], provider: str = "fixture"):
        for b in bars:
            existing = self.db.query(MarketBar).filter(
                MarketBar.instrument_id == instrument_id,
                MarketBar.timestamp == b.timestamp
            ).first()
            if not existing:
                db_bar = MarketBar(
                    instrument_id=instrument_id,
                    timestamp=b.timestamp,
                    open=b.open,
                    high=b.high,
                    low=b.low,
                    close=b.close,
                    adjusted_close=b.adjusted_close or b.close,
                    volume=b.volume,
                    provider=provider,
                    is_validated=True
                )
                self.db.add(db_bar)
        self.db.commit()
