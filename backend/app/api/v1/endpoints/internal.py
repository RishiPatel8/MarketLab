from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.db.session import get_sync_db
from app.db.models.report import AutomationEvent
from app.core.security import verify_internal_automation_token
from app.services.market_data_service import MarketDataService
from app.services.instrument_service import InstrumentService

router = APIRouter()

@router.post("/ingestion-jobs")
def trigger_ingestion_job(
    payload: Dict[str, Any],
    db: Session = Depends(get_sync_db),
    auth: bool = Depends(verify_internal_automation_token)
):
    """
    Triggered by n8n or scheduled cron workflows to ingest latest daily market data.
    Strictly protected by X-Internal-Token.
    """
    symbol = payload.get("symbol", "GREENPOWER")
    exchange = payload.get("exchange", "NSE")

    inst_svc = InstrumentService(db)
    inst = inst_svc.repo.get_by_symbol_and_exchange(symbol, exchange)

    md_svc = MarketDataService(db)
    bars, val = md_svc.get_and_validate_bars(symbol=symbol, exchange=exchange, instrument_id=inst.id if inst else None)

    # Record automation event
    evt = AutomationEvent(
        workflow_name="market_data_ingestion",
        related_run_id=None,
        status="succeeded" if val.is_valid else "failed",
        payload_json=json.dumps(payload),
        error_summary="; ".join(val.issues) if not val.is_valid else None
    )
    db.add(evt)
    db.commit()

    return {
        "status": "success",
        "symbol": symbol,
        "exchange": exchange,
        "bars_ingested": len(bars),
        "validation_passed": val.is_valid
    }

@router.post("/automation-events")
def record_automation_event(
    payload: Dict[str, Any],
    db: Session = Depends(get_sync_db),
    auth: bool = Depends(verify_internal_automation_token)
):
    """
    Receives automation notifications and trigger records from n8n.
    """
    evt = AutomationEvent(
        workflow_name=payload.get("workflow_name", "n8n_event"),
        related_run_id=payload.get("run_id"),
        status=payload.get("status", "received"),
        payload_json=json.dumps(payload),
        error_summary=payload.get("error")
    )
    db.add(evt)
    db.commit()

    return {"status": "recorded", "event_id": evt.id}
