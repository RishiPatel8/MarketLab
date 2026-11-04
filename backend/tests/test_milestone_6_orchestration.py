import pytest
from app.agents.graph import research_graph
from app.agents.state import ResearchWorkflowState
from app.agents.nodes.planner import parse_investment_intent

def test_intent_parsing_natural_language():
    """Verify natural language extraction of amount, horizon, and risk."""
    parsed1 = parse_investment_intent("I want to invest ₹50,000 in Reliance Industries for six months. Conservative approach.")
    assert parsed1["amount"] == 50000.0
    assert parsed1["days"] == 180
    assert parsed1["category"] == "medium_term"
    assert parsed1["risk"] == "conservative"

    parsed2 = parse_investment_intent("Swing trade 25000 INR in Tata Motors for 1 month with aggressive risk")
    assert parsed2["amount"] == 25000.0
    assert parsed2["days"] == 30
    assert parsed2["category"] == "short_term"
    assert parsed2["risk"] == "aggressive"

def test_full_langgraph_workflow_with_decision_intelligence(db_session):
    """Verify complete end-to-end multi-agent LangGraph execution producing BUY/HOLD/SELL and targets."""
    state: ResearchWorkflowState = {
        "run_id": "test-run-m6-reliance",
        "user_id": None,
        "original_question": "I want to invest ₹50,000 in Reliance Industries for six months. Run strategies and evaluate entry.",
        "investment_amount_inr": 50000.0,
        "horizon_days": 180,
        "horizon_category": "medium_term",
        "risk_tolerance": "moderate",
        "instrument_candidates": [],
        "resolved_instrument": None,
        "research_spec": None,
        "market_data_reference": None,
        "data_validation": None,
        "financial_facts": None,
        "fundamental_analysis": None,
        "retrieved_evidence": [],
        "quantitative_results": None,
        "technical_analysis": None,
        "strategy_consensus": None,
        "verification_findings": None,
        "decision_result": None,
        "retry_count": 0,
        "run_status": "running",
        "current_step": "planner",
        "error_message": None,
        "final_report": None
    }

    final_state = research_graph.invoke(state)

    assert final_state["run_status"] in ("completed", "completed_with_limitations")
    rep = final_state.get("final_report")
    assert rep is not None
    assert rep["decision_rating"] in ("BUY", "HOLD", "SELL", "INSUFFICIENT_EVIDENCE")
    assert rep["entry_price_min"] > 0
    assert rep["entry_price_max"] >= rep["entry_price_min"]
    assert rep["stop_loss_price"] > 0
    assert len(rep["scenario_projections"]) == 3
    assert rep["strategy_consensus"] is not None
    assert "SEBI" in rep["report_markdown"]
