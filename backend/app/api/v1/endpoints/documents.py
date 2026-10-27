from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_sync_db
from app.schemas.document import DocumentIngestRequest, DocumentResponse
from app.services.rag_service import RAGService
from app.core.security import get_current_user_or_api_key

router = APIRouter()

@router.post("/ingest", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def ingest_document(
    req: DocumentIngestRequest,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """
    Ingests an approved corporate filing, annual report, or regulatory disclosure.
    Generates semantic chunks and vector embeddings.
    """
    service = RAGService(db)
    return service.ingest_document(req)
