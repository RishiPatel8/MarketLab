import logging
from datetime import datetime, timezone
from app.db.session import SyncSessionLocal
from app.db.models.research_run import ResearchRun
from app.agents.graph import research_graph
from app.agents.state import ResearchWorkflowState

logger = logging.getLogger("marketlab.worker")

def execute_research_workflow(run_id: str):
    """
    Executes the complete LangGraph research workflow for the specified run_id.
    Updates progress and final state in the database.
    """
    logger.info(f"Starting research execution for run_id: {run_id}")
    with SyncSessionLocal() as db:
        run_obj = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
        if not run_obj:
            logger.error(f"Research run {run_id} not found in database.")
            return

        run_obj.status = "running"
        run_obj.current_step = "planner"
        run_obj.progress_percentage = 10
        db.commit()

        question = run_obj.research_question

    initial_state: ResearchWorkflowState = {
        "run_id": run_id,
        "user_id": None,
        "original_question": question,
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
        "run_status": "running",
        "current_step": "planner",
        "error_message": None,
        "final_report": None
    }

    try:
        final_state = research_graph.invoke(initial_state)
        logger.info(f"Research run {run_id} finished with status: {final_state.get('run_status')}")

        with SyncSessionLocal() as db:
            run_obj = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
            if run_obj:
                run_obj.status = final_state.get("run_status", "completed")
                run_obj.current_step = final_state.get("current_step", "completed")
                run_obj.progress_percentage = 100 if run_obj.status in ("completed", "completed_with_limitations") else 50
                run_obj.error_message = final_state.get("error_message")
                resolved = final_state.get("resolved_instrument")
                if resolved and "id" in resolved:
                    run_obj.resolved_instrument_id = resolved["id"]
                db.commit()

    except Exception as e:
        logger.exception(f"Error during research execution for run_id {run_id}: {e}")
        with SyncSessionLocal() as db:
            run_obj = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
            if run_obj:
                run_obj.status = "failed"
                run_obj.error_message = str(e)
                run_obj.completed_at = datetime.now(timezone.utc)
                db.commit()
