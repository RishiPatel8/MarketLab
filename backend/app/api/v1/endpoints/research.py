from typing import List, Optional
import json
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from app.db.session import get_sync_db
from app.db.models.research_run import ResearchRun, ResearchSource
from app.db.models.report import Report
from app.db.models.instrument import Instrument
from app.schemas.research import ResearchRequest, ResearchRunResponse, ResearchRunSummary
from app.schemas.report import ResearchReportResponse
from app.core.security import get_current_user_or_api_key
from app.worker.tasks import execute_research_workflow

router = APIRouter()

@router.post("", response_model=ResearchRunResponse, status_code=status.HTTP_202_ACCEPTED)
def create_research_run(
    req: ResearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """
    Initiates an asynchronous research workflow.
    Validates the query, creates a queued research run, and schedules execution.
    """
    run_id = str(uuid.uuid4())
    spec_preview = {
        "question": req.question,
        "symbol": req.symbol,
        "exchange": req.exchange,
        "horizon_days": req.horizon_days
    }

    db_run = ResearchRun(
        id=run_id,
        user_id=user["user_id"],
        research_question=req.question,
        structured_specification=json.dumps(spec_preview),
        status="queued",
        current_step="planner",
        progress_percentage=0
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)

    # Trigger background execution asynchronously
    background_tasks.add_task(execute_research_workflow, run_id)

    return ResearchRunResponse(
        run_id=db_run.id,
        status=db_run.status,
        current_step=db_run.current_step,
        progress_percentage=db_run.progress_percentage,
        message="Research workflow queued successfully",
        created_at=db_run.created_at
    )

@router.get("", response_model=List[ResearchRunSummary])
def list_research_runs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Lists research history with pagination."""
    runs = db.query(ResearchRun).order_by(ResearchRun.created_at.desc()).offset(skip).limit(limit).all()
    return [
        ResearchRunSummary(
            id=r.id,
            research_question=r.research_question,
            status=r.status,
            current_step=r.current_step,
            progress_percentage=r.progress_percentage,
            resolved_instrument_id=r.resolved_instrument_id,
            verification_status=r.verification_status,
            created_at=r.created_at,
            completed_at=r.completed_at
        ) for r in runs
    ]

@router.get("/{run_id}", response_model=ResearchRunResponse)
def get_research_run_status(
    run_id: str,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Retrieves current status, step, and progress for a research run."""
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Research run {run_id} not found")

    resolved_info = None
    if run.resolved_instrument_id:
        inst = db.query(Instrument).filter(Instrument.id == run.resolved_instrument_id).first()
        if inst:
            resolved_info = {
                "id": inst.id,
                "symbol": inst.symbol,
                "company_name": inst.company_name,
                "exchange": inst.exchange
            }

    return ResearchRunResponse(
        run_id=run.id,
        status=run.status,
        current_step=run.current_step,
        progress_percentage=run.progress_percentage,
        resolved_instrument=resolved_info,
        verification_status=run.verification_status,
        error_message=run.error_message,
        created_at=run.created_at,
        completed_at=run.completed_at
    )

@router.get("/{run_id}/report", response_model=ResearchReportResponse)
def get_research_report(
    run_id: str,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Retrieves the generated research report, citations, and metrics."""
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Research run {run_id} not found")

    report = db.query(Report).filter(Report.research_run_id == run_id).first()
    if not report:
        if run.status in ("queued", "running"):
            raise HTTPException(status_code=409, detail="Research report is still generating.")
        raise HTTPException(status_code=404, detail="No report found for this research run.")

    inst = db.query(Instrument).filter(Instrument.id == run.resolved_instrument_id).first() if run.resolved_instrument_id else None
    sources = db.query(ResearchSource).filter(ResearchSource.research_run_id == run_id).all()

    return ResearchReportResponse(
        report_id=report.id,
        run_id=run.id,
        instrument={
            "symbol": inst.symbol if inst else "N/A",
            "company_name": inst.company_name if inst else "N/A",
            "exchange": inst.exchange if inst else "NSE"
        },
        research_question=run.research_question,
        sentiment_label=report.sentiment_label,
        report_timestamp=report.created_at,
        data_coverage={"status": "validated", "total_bars": 260},
        executive_summary=report.executive_summary,
        business_financial_analysis=report.business_financial_analysis,
        technical_analysis=report.technical_analysis,
        positive_evidence=json.loads(report.positive_evidence_json) if report.positive_evidence_json else [],
        negative_evidence=json.loads(report.negative_evidence_json) if report.negative_evidence_json else [],
        key_risks=json.loads(report.key_risks_json) if report.key_risks_json else [],
        sources=[
            {
                "source_title": s.source_title,
                "source_url_or_identifier": s.source_url_or_identifier,
                "publication_date": s.publication_date.isoformat() if s.publication_date else None,
                "page_or_section": s.page_or_section,
                "citation_text": s.citation_text,
                "confidence_score": s.confidence_score
            } for s in sources
        ],
        verification=json.loads(report.verification_findings_json) if report.verification_findings_json else {},
        limitations=json.loads(report.limitations_json) if report.limitations_json else [],
        report_markdown=report.report_content_markdown,
        is_completed_with_limitations=(run.status == "completed_with_limitations")
    )
