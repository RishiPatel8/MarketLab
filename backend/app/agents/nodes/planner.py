from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from app.agents.state import ResearchWorkflowState
from app.schemas.research import ResearchSpecification
from app.services.instrument_service import InstrumentService
from app.db.session import SyncSessionLocal

def planner_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    """
    Supervisor / Planner Node:
    Resolves the target instrument, checks for ambiguity, and formulates
    the structured research specification.
    """
    question = state["original_question"]
    resolved = state.get("resolved_instrument")
    candidates = state.get("instrument_candidates") or []

    # If instrument is not already resolved, attempt resolution
    if not resolved:
        with SyncSessionLocal() as db:
            inst_service = InstrumentService(db)
            res = inst_service.resolve_instrument(question)
            if res.requires_clarification:
                return {
                    "instrument_candidates": [c.dict() for c in res.candidates],
                    "run_status": "needs_clarification",
                    "current_step": "planner",
                    "error_message": res.message
                }
            elif not res.resolved:
                return {
                    "run_status": "failed",
                    "current_step": "planner",
                    "error_message": res.message
                }
            resolved = res.instrument.model_dump()

    # Formulate structured specification
    now = datetime.now(timezone.utc)
    spec = ResearchSpecification(
        research_id=state["run_id"],
        original_question=question,
        symbol=resolved["symbol"],
        company_name=resolved["company_name"],
        exchange=resolved["exchange"],
        horizon_days=180,
        start_date=now - timedelta(days=365),
        end_date=now
    )

    return {
        "resolved_instrument": resolved,
        "research_spec": spec.model_dump(),
        "run_status": "running",
        "current_step": "market_data_retrieval"
    }
