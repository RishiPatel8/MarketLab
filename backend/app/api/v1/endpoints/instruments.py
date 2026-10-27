from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_sync_db
from app.services.instrument_service import InstrumentService
from app.services.market_data_service import MarketDataService
from app.schemas.instrument import InstrumentResponse, InstrumentResolutionResult
from app.schemas.market_data import MarketDataResponse, MarketBarSchema

router = APIRouter()

@router.get("/search", response_model=List[InstrumentResponse])
def search_instruments(
    q: str = Query(..., min_length=1, description="Company name or ticker query"),
    limit: int = 10,
    db: Session = Depends(get_sync_db)
):
    """Searches instruments by ticker symbol or company name."""
    service = InstrumentService(db)
    return service.search_instruments(q, limit=limit)

@router.get("/resolve", response_model=InstrumentResolutionResult)
def resolve_instrument(
    q: str = Query(..., description="Query phrase e.g. 'Orient Green Power' or 'Tata'"),
    db: Session = Depends(get_sync_db)
):
    """Resolves a natural language query to an instrument with ambiguity check."""
    service = InstrumentService(db)
    return service.resolve_instrument(q)

@router.get("/{instrument_id}", response_model=InstrumentResponse)
def get_instrument_by_id(
    instrument_id: str,
    db: Session = Depends(get_sync_db)
):
    """Retrieves authoritative instrument metadata."""
    service = InstrumentService(db)
    inst = service.get_by_id(instrument_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return inst

@router.get("/{instrument_id}/market-data", response_model=MarketDataResponse)
def get_instrument_market_data(
    instrument_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_sync_db)
):
    """Retrieves validated historical market data for the instrument."""
    inst_service = InstrumentService(db)
    inst = inst_service.get_by_id(instrument_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")

    md_service = MarketDataService(db)
    bars, validation = md_service.get_and_validate_bars(
        symbol=inst.symbol,
        exchange=inst.exchange,
        start_date=start_date,
        end_date=end_date,
        instrument_id=inst.id
    )

    return MarketDataResponse(
        instrument_id=inst.id,
        symbol=inst.symbol,
        exchange=inst.exchange,
        validation=validation,
        bars=bars
    )
