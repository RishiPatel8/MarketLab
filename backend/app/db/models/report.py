import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from app.db.session import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    research_run_id = Column(String(36), ForeignKey("research_runs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=False)
    sentiment_label = Column(String(50), default="neutral")  # bullish, neutral, bearish, inconclusive
    report_content_markdown = Column(Text, nullable=False)
    business_financial_analysis = Column(Text, nullable=True)
    technical_analysis = Column(Text, nullable=True)
    positive_evidence_json = Column(Text, nullable=True)  # JSON array
    negative_evidence_json = Column(Text, nullable=True)  # JSON array
    key_risks_json = Column(Text, nullable=True)  # JSON array
    verification_findings_json = Column(Text, nullable=True)  # JSON object
    limitations_json = Column(Text, nullable=True)  # JSON array
    report_version = Column(String(20), default="1.0.0")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class AutomationEvent(Base):
    __tablename__ = "automation_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_name = Column(String(100), nullable=False, index=True)
    related_run_id = Column(String(36), nullable=True, index=True)
    status = Column(String(50), nullable=False)  # triggered, succeeded, failed
    attempt_count = Column(String(10), default="1")
    payload_json = Column(Text, nullable=True)
    error_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
