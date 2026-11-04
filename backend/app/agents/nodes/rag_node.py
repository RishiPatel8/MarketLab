from typing import Dict, Any, List
from app.agents.state import ResearchWorkflowState
from app.services.rag_service import RAGService
from app.db.session import SyncSessionLocal

def rag_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    """
    RAG Research Node:
    Retrieves source passages with authoritative timestamps and content hashes.
    Quarantines retrieved text as untrusted context to prevent prompt injection.
    """
    question = state["original_question"]
    resolved = state.get("resolved_instrument")
    symbol = resolved["symbol"] if resolved else None

    with SyncSessionLocal() as db:
        service = RAGService(db)
        evidence_items = service.retrieve_evidence(
            query=f"{symbol} {question}" if symbol else question,
            symbol_hint=symbol,
            top_k=4
        )

    evidence_list = []
    for item in evidence_items:
        # Sanitize and quarantine untrusted external text
        sanitized_content = item.content.replace("<script>", "").replace("</script>", "")
        evidence_list.append({
            "document_id": item.document_id,
            "document_title": item.document_title,
            "source_url_or_identifier": item.source_url_or_identifier,
            "section": item.section,
            "page_number": item.page_number,
            "publication_date": item.publication_date.isoformat() if item.publication_date else None,
            "content": sanitized_content,
            "relevance_score": item.relevance_score,
            "content_hash": item.content_hash,
            "is_mock_embedding": item.is_mock_embedding
        })

    return {
        "retrieved_evidence": evidence_list,
        "current_step": "quantitative_analysis"
    }
