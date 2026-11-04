from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_sync_db
from app.core.security import get_current_user_or_api_key
from app.services.instrument_service import InstrumentService
from app.services.market_data_service import MarketDataService
from app.schemas.instrument import (
    InstrumentResponse,
    InstrumentResolutionResult,
    PaginatedInstrumentsResponse,
    InstrumentSyncStatusResponse
)
from app.schemas.market_data import MarketDataResponse, MarketBarSchema, MarketDataValidationResult

router = APIRouter()

@router.get("/search", response_model=PaginatedInstrumentsResponse)
def search_instruments(
    q: str = Query("", description="Company name, ticker, BSE code, ISIN, or scheme name"),
    instrument_type: str = Query("ALL", description="Filter: ALL, EQUITY, SME_EQUITY, ETF, MUTUAL_FUND"),
    exchange: str = Query("ALL", description="Filter: ALL, NSE, BSE, AMFI"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_sync_db)
):
    """
    Unified instrument search across the entire Indian universe:
    NSE equities, BSE-exclusive stocks, SMEs, ETFs, and AMFI mutual funds.
    """
    service = InstrumentService(db)
    return service.search_instruments(
        query=q,
        instrument_type=instrument_type,
        exchange=exchange,
        page=page,
        limit=limit
    )

@router.get("/resolve", response_model=InstrumentResolutionResult)
def resolve_instrument(
    q: str = Query(..., description="Query phrase e.g. 'Orient Green Power', 'Tata', or ticker 'RELIANCE'"),
    db: Session = Depends(get_sync_db)
):
    """
    Resolves a natural language query or ticker to an authoritative instrument with ambiguity check.
    Prevents silent substitution and returns candidate matches if ambiguous.
    """
    service = InstrumentService(db)
    return service.resolve_instrument(q)

@router.get("/sync/status", response_model=InstrumentSyncStatusResponse)
def get_instrument_sync_status(
    db: Session = Depends(get_sync_db)
):
    """
    Returns administrative status and authoritative coverage metrics for the Indian instrument universe.
    """
    service = InstrumentService(db)
    return service.get_sync_status()

@router.post("/sync/trigger")
def trigger_instrument_sync(
    current_user: dict = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_sync_db)
):
    """
    Authorized endpoint to trigger an on-demand synchronization against official NSE, BSE, and AMFI references.
    """
    service = InstrumentService(db)
    result = service.trigger_sync()
    return {
        "status": "SUCCESS",
        "details": result,
        "triggered_by": current_user.get("user_id")
    }

@router.get("/{instrument_id}", response_model=InstrumentResponse)
def get_instrument_by_id(
    instrument_id: str,
    db: Session = Depends(get_sync_db)
):
    """Retrieves authoritative instrument metadata by internal ID."""
    service = InstrumentService(db)
    inst = service.get_by_id(instrument_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instrument not found")
    return inst

@router.get("/{instrument_id}/market-data", response_model=MarketDataResponse)
def get_instrument_market_data(
    instrument_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_sync_db)
):
    """
    Retrieves validated historical market data for the instrument.
    Distinguishes discovery from price-data availability.
    """
    inst_service = InstrumentService(db)
    inst = inst_service.get_by_id(instrument_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instrument not found")

    # Mutual fund handling
    if inst.instrument_type == "MUTUAL_FUND":
        val = MarketDataValidationResult(
            is_valid=True,
            total_bars=1 if inst.latest_nav else 0,
            coverage_percentage=100.0 if inst.latest_nav else 0.0,
            anomalies_detected=0,
            provider_attribution="AMFI",
            latency_type="nav_observation",
            data_frequency="nav_observation",
            latest_observation_time=inst.latest_nav_date,
            retrieval_timestamp=datetime.now(),
            issues=[] if inst.latest_nav else ["Latest NAV not currently observed from AMFI"]
        )
        bars = []
        if inst.latest_nav and inst.latest_nav > 0:
            bars.append(MarketBarSchema(
                timestamp=inst.latest_nav_date or datetime.now(),
                open=inst.latest_nav,
                high=inst.latest_nav,
                low=inst.latest_nav,
                close=inst.latest_nav,
                adjusted_close=inst.latest_nav,
                volume=0.0,
                provider="AMFI"
            ))
        return MarketDataResponse(
            instrument_id=inst.id,
            symbol=inst.symbol,
            exchange=inst.exchange,
            validation=val,
            bars=bars
        )

    md_service = MarketDataService(db)
    bars, validation = md_service.get_and_validate_bars(
        symbol=inst.symbol,
        exchange="NSE" if "NSE" in inst.exchange else "BSE",
        start_date=start_date,
        end_date=end_date,
        instrument_id=inst.id
    )

    # Check if price provider has data
    if not bars:
        val_unavail = MarketDataValidationResult(
            is_valid=False,
            total_bars=0,
            coverage_percentage=0.0,
            anomalies_detected=1,
            provider_attribution=validation.provider_attribution if validation else "yfinance",
            latency_type="daily_historical",
            data_frequency="daily_historical",
            issues=["Instrument found in official master. Price data unavailable from configured provider."],
            latest_observation_time=None,
            retrieval_timestamp=datetime.now()
        )
        return MarketDataResponse(
            instrument_id=inst.id,
            symbol=inst.symbol,
            exchange=inst.exchange,
            validation=val_unavail,
            bars=[]
        )

    return MarketDataResponse(
        instrument_id=inst.id,
        symbol=inst.symbol,
        exchange=inst.exchange,
        validation=validation,
        bars=[
            MarketBarSchema(
                timestamp=b.timestamp,
                open=b.open,
                high=b.high,
                low=b.low,
                close=b.close,
                volume=b.volume,
                provider=b.provider
            ) for b in bars
        ]
    )
