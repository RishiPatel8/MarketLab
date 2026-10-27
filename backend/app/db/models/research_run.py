import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float, Index
from app.db.session import Base

class ResearchRun(Base):
    __tablename__ = "research_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    research_question = Column(Text, nullable=False)
    structured_specification = Column(Text, nullable=True)  # JSON serialized ResearchSpecification
    status = Column(String(50), nullable=False, default="queued", index=True)
    # queued, running, completed, completed_with_limitations, needs_clarification, failed
    current_step = Column(String(50), default="planner")
    progress_percentage = Column(Integer, default=0)
    resolved_instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=True, index=True)
    retry_count = Column(Integer, default=0)
    verification_status = Column(String(50), default="pending")  # verified, flagged, insufficient_evidence
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    completed_at = Column(DateTime, nullable=True)


class ResearchSource(Base):
    __tablename__ = "research_sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    research_run_id = Column(String(36), ForeignKey("research_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    source_title = Column(String(255), nullable=False)
    source_url_or_identifier = Column(String(500), nullable=False)
    publication_date = Column(DateTime, nullable=True)
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    citation_text = Column(Text, nullable=False)
    page_or_section = Column(String(100), nullable=True)
    confidence_score = Column(Float, default=1.0)
