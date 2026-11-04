from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, case
from app.db.models.instrument import Instrument
from app.schemas.instrument import InstrumentCreate

class InstrumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, instrument_id: str) -> Optional[Instrument]:
        return self.db.query(Instrument).filter(Instrument.id == instrument_id).first()

    def get_by_symbol_and_exchange(self, symbol: str, exchange: Optional[str] = None) -> Optional[Instrument]:
        query = self.db.query(Instrument).filter(
            or_(
                Instrument.symbol.ilike(symbol),
                Instrument.nse_symbol.ilike(symbol),
                Instrument.bse_symbol.ilike(symbol),
                Instrument.bse_code == symbol
            )
        )
        if exchange and exchange.upper() != "ALL":
            query = query.filter(Instrument.exchange.like(f"%{exchange.upper()}%"))
        return query.first()

    def get_by_isin(self, isin: str) -> Optional[Instrument]:
        return self.db.query(Instrument).filter(Instrument.isin.ilike(isin.strip())).first()

    def get_by_bse_code(self, bse_code: str) -> Optional[Instrument]:
        return self.db.query(Instrument).filter(Instrument.bse_code == bse_code.strip()).first()

    def get_by_scheme_code(self, scheme_code: str) -> Optional[Instrument]:
        return self.db.query(Instrument).filter(Instrument.scheme_code == scheme_code.strip()).first()

    def search_advanced(
        self,
        query_str: str,
        instrument_type: Optional[str] = None,
        exchange: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Instrument], int]:
        """
        Multi-field search across company name, symbol, BSE scrip code, ISIN, scheme code, AMC, and aliases.
        Ranks exact matches and prefix matches above general substring matches.
        """
        raw_q = query_str.strip()
        q_upper = raw_q.upper()
        like_pattern = f"%{raw_q}%"
        prefix_pattern = f"{raw_q}%"

        # Match conditions across all identifier fields
        match_conditions = or_(
            Instrument.symbol.ilike(like_pattern),
            Instrument.company_name.ilike(like_pattern),
            Instrument.canonical_name.ilike(like_pattern),
            Instrument.nse_symbol.ilike(like_pattern),
            Instrument.bse_code == raw_q,
            Instrument.bse_symbol.ilike(like_pattern),
            Instrument.isin.ilike(raw_q),
            Instrument.scheme_code == raw_q,
            Instrument.amc_or_issuer.ilike(like_pattern),
            Instrument.aliases.ilike(like_pattern)
        )

        base_query = self.db.query(Instrument).filter(match_conditions)

        # Apply instrument_type filter
        if instrument_type and instrument_type.upper() != "ALL":
            base_query = base_query.filter(Instrument.instrument_type == instrument_type.upper())

        # Apply exchange filter
        if exchange and exchange.upper() != "ALL":
            base_query = base_query.filter(Instrument.exchange.like(f"%{exchange.upper()}%"))

        total_count = base_query.count()

        # Priority ranking expression:
        # 1. Exact symbol, ISIN, BSE code, or scheme code (rank 1)
        # 2. Symbol prefix match (rank 2)
        # 3. Company name prefix match (rank 3)
        # 4. Other matches (rank 4)
        rank_case = case(
            (or_(
                Instrument.symbol.ilike(raw_q),
                Instrument.nse_symbol.ilike(raw_q),
                Instrument.bse_code == raw_q,
                Instrument.isin.ilike(raw_q),
                Instrument.scheme_code == raw_q
            ), 1),
            (or_(
                Instrument.symbol.ilike(prefix_pattern),
                Instrument.nse_symbol.ilike(prefix_pattern)
            ), 2),
            (Instrument.company_name.ilike(prefix_pattern), 3),
            else_=4
        )

        offset = max(0, (page - 1) * limit)
        results = base_query.order_by(rank_case, Instrument.company_name).offset(offset).limit(limit).all()
        return results, total_count

    def search(self, query: str, limit: int = 10) -> List[Instrument]:
        results, _ = self.search_advanced(query, limit=limit)
        return results

    def create(self, instrument_in: InstrumentCreate) -> Instrument:
        db_obj = Instrument(
            exchange=instrument_in.exchange.upper(),
            symbol=instrument_in.symbol.upper(),
            company_name=instrument_in.company_name,
            canonical_name=instrument_in.canonical_name or instrument_in.company_name,
            display_name=instrument_in.display_name,
            instrument_type=instrument_in.instrument_type,
            currency=instrument_in.currency,
            sector=instrument_in.sector,
            industry=instrument_in.industry,
            isin=instrument_in.isin,
            nse_symbol=instrument_in.nse_symbol,
            bse_code=instrument_in.bse_code,
            bse_symbol=instrument_in.bse_symbol,
            scheme_code=instrument_in.scheme_code,
            amc_or_issuer=instrument_in.amc_or_issuer,
            scheme_category=instrument_in.scheme_category,
            plan_type=instrument_in.plan_type,
            option_type=instrument_in.option_type,
            latest_nav=instrument_in.latest_nav,
            latest_nav_date=instrument_in.latest_nav_date,
            status=instrument_in.status,
            source_provider=instrument_in.source_provider,
            data_availability=instrument_in.data_availability
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_all(self, limit: int = 50) -> List[Instrument]:
        return self.db.query(Instrument).limit(limit).all()
