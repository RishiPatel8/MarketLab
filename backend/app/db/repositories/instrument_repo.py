from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, select
from app.db.models.instrument import Instrument
from app.schemas.instrument import InstrumentCreate

class InstrumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, instrument_id: str) -> Optional[Instrument]:
        return self.db.query(Instrument).filter(Instrument.id == instrument_id).first()

    def get_by_symbol_and_exchange(self, symbol: str, exchange: str = "NSE") -> Optional[Instrument]:
        return self.db.query(Instrument).filter(
            Instrument.symbol.ilike(symbol),
            Instrument.exchange.ilike(exchange)
        ).first()

    def search(self, query: str, limit: int = 10) -> List[Instrument]:
        q = f"%{query.strip()}%"
        return self.db.query(Instrument).filter(
            or_(
                Instrument.symbol.ilike(q),
                Instrument.company_name.ilike(q)
            )
        ).limit(limit).all()

    def create(self, instrument_in: InstrumentCreate) -> Instrument:
        db_obj = Instrument(
            exchange=instrument_in.exchange.upper(),
            symbol=instrument_in.symbol.upper(),
            company_name=instrument_in.company_name,
            instrument_type=instrument_in.instrument_type,
            currency=instrument_in.currency,
            sector=instrument_in.sector,
            industry=instrument_in.industry,
            isin=instrument_in.isin,
            provider_identifier=instrument_in.provider_identifier
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_all(self, limit: int = 50) -> List[Instrument]:
        return self.db.query(Instrument).limit(limit).all()
