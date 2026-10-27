from typing import Dict, Any
from app.agents.state import ResearchWorkflowState
from app.services.market_data_service import MarketDataService
from app.db.session import SyncSessionLocal

def market_data_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    """
    Market Data Retrieval & Validation Node:
    Retrieves historical OHLCV bars, verifies pricing integrity, and records validation metrics.
    """
    resolved = state.get("resolved_instrument")
    if not resolved:
        return {
            "run_status": "failed",
            "current_step": "market_data_retrieval",
            "error_message": "Cannot retrieve market data: instrument not resolved."
        }

    symbol = resolved["symbol"]
    exchange = resolved.get("exchange", "NSE")
    inst_id = resolved.get("id")

    with SyncSessionLocal() as db:
        service = MarketDataService(db)
        bars, validation = service.get_and_validate_bars(
            symbol=symbol,
            exchange=exchange,
            instrument_id=inst_id
        )

    market_ref = {
        "symbol": symbol,
        "exchange": exchange,
        "total_bars": len(bars),
        "start_date": bars[0].timestamp.isoformat() if bars else None,
        "end_date": bars[-1].timestamp.isoformat() if bars else None,
        "latest_close": bars[-1].close if bars else None,
        "provider": validation.provider_attribution
    }

    return {
        "market_data_reference": market_ref,
        "data_validation": validation.model_dump(),
        "current_step": "financial_research"
    }
