from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class DocumentIngestRequest(BaseModel):
    title: str = Field(..., min_length=2)
    source_type: str = Field(..., description="annual_report, quarterly_filing, disclosure, press_release")
    source_url: Optional[str] = None
    publisher: str = Field(default="Company")
    publication_date: datetime = Field(default_factory=datetime.utcnow)
    instrument_symbol: Optional[str] = None
    raw_text: str = Field(..., min_length=20)

class DocumentChunkResponse(BaseModel):
    chunk_index: int
    content: str
    section: Optional[str] = None
    page_number: Optional[int] = None

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    source_type: str
    source_url: Optional[str] = None
    publisher: str
    publication_date: datetime
    content_hash: str
    chunk_count: int
    created_at: datetime

class RetrievedEvidenceItem(BaseModel):
    document_id: str
    document_title: str
    source_url_or_identifier: str
    section: Optional[str] = None
    page_number: Optional[int] = None
    publication_date: Optional[datetime] = None
    content: str
    relevance_score: float
    content_hash: str
    is_mock_embedding: bool = False
