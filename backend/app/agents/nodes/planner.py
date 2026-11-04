import re
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from app.agents.state import ResearchWorkflowState
from app.schemas.research import ResearchSpecification
from app.services.instrument_service import InstrumentService
from app.db.session import SyncSessionLocal

def parse_investment_intent(text: str) -> Dict[str, Any]:
    """Extracts investment amount, horizon, and risk profile from natural language prompts."""
    # 1. Amount extraction (e.g., ₹50,000, Rs 50000, 100000 INR)
    amt = 50000.0
    amt_match = re.search(r"(?:₹|rs\.?|inr)\s*([\d,]+)", text, re.IGNORECASE)
    if not amt_match:
        amt_match = re.search(r"([\d,]+)\s*(?:rupees|inr)", text, re.IGNORECASE)
    if amt_match:
        try:
            amt = float(amt_match.group(1).replace(",", ""))
        except ValueError:
            amt = 50000.0

    # 2. Horizon extraction (e.g. 6 months, 1 year, 30 days)
    days = 180
    cat = "medium_term"
    if re.search(r"(?:one|1)\s*year|12\s*months", text, re.IGNORECASE):
        days = 365
        cat = "long_term"
    elif re.search(r"(?:six|6)\s*months", text, re.IGNORECASE):
        days = 180
        cat = "medium_term"
    elif re.search(r"(?:three|3)\s*months", text, re.IGNORECASE):
        days = 90
        cat = "medium_term"
    elif re.search(r"(?:one|1)\s*month|30\s*days", text, re.IGNORECASE):
        days = 30
        cat = "short_term"
    elif re.search(r"(?:short[\s-]term|swing|few\s*days)", text, re.IGNORECASE):
        days = 20
        cat = "short_term"

    # 3. Risk tolerance
    risk = "moderate"
    if re.search(r"conservative|low[\s-]risk|safe", text, re.IGNORECASE):
        risk = "conservative"
    elif re.search(r"aggressive|high[\s-]risk", text, re.IGNORECASE):
        risk = "aggressive"

    return {
        "amount": amt,
        "days": days,
        "category": cat,
        "risk": risk
    }

def planner_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    """
    Supervisor / Planner Node:
    Resolves the target instrument, checks for ambiguity, extracts structured intent,
    and formulates the comprehensive research specification.
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

    # Parse investment intent
    parsed = parse_investment_intent(question)
    inv_amt = state.get("investment_amount_inr") or parsed["amount"]
    horizon_days = state.get("horizon_days") or parsed["days"]
    horizon_cat = state.get("horizon_category") or parsed["category"]
    risk_tol = state.get("risk_tolerance") or parsed["risk"]

    # Formulate structured specification
    now = datetime.now(timezone.utc)
    spec = ResearchSpecification(
        research_id=state["run_id"],
        original_question=question,
        symbol=resolved["symbol"],
        company_name=resolved["company_name"],
        exchange=resolved["exchange"],
        investment_amount_inr=inv_amt,
        horizon_days=horizon_days,
        horizon_category=horizon_cat,
        risk_tolerance=risk_tol,
        start_date=now - timedelta(days=max(365, horizon_days + 180)),
        end_date=now
    )

    return {
        "resolved_instrument": resolved,
        "research_spec": spec.model_dump(),
        "investment_amount_inr": inv_amt,
        "horizon_days": horizon_days,
        "horizon_category": horizon_cat,
        "risk_tolerance": risk_tol,
        "run_status": "running",
        "current_step": "market_data_retrieval"
    }
