import pytest
import uuid
from app.agents.graph import research_graph
from app.agents.state import ResearchWorkflowState

def test_full_langgraph_workflow_execution():
    run_id = str(uuid.uuid4())
    initial_state: ResearchWorkflowState = {
        "run_id": run_id,
        "user_id": None,
        "original_question": "Research Orient Green Power for a six-month horizon",
        "instrument_candidates": [],
        "resolved_instrument": None,
        "research_spec": None,
        "market_data_reference": None,
        "data_validation": None,
        "financial_facts": None,
        "retrieved_evidence": [],
        "quantitative_results": None,
        "verification_findings": None,
        "retry_count": 0,
        "run_status": "queued",
        "current_step": "planner",
        "error_message": None,
        "final_report": None
    }

    final_state = research_graph.invoke(initial_state)

    assert final_state["run_status"] in ("completed", "completed_with_limitations")
    assert final_state["resolved_instrument"]["symbol"] == "GREENPOWER"
    assert final_state["market_data_reference"]["total_bars"] > 100
    assert len(final_state["retrieved_evidence"]) > 0
    assert final_state["quantitative_results"] is not None
    assert final_state["final_report"] is not None
    assert "report_markdown" in final_state["final_report"]
    assert len(final_state["final_report"]["sources"]) > 0
