import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Index
from app.db.session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # annual_report, quarterly_filing, disclosure, press_release
    source_url = Column(String(500), nullable=True)
    publisher = Column(String(100), nullable=False)  # BSE, NSE, Company
    publication_date = Column(DateTime, nullable=False)
    content_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    section = Column(String(100), nullable=True)
    page_number = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)  # Stored JSON string
    embedding_json = Column(Text, nullable=True)  # Stored float array serialized as JSON
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_doc_chunk_idx", "document_id", "chunk_index", unique=True),
    )
