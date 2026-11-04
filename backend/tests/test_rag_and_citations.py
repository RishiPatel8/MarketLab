import pytest
from app.rag.chunker import TextChunker
from app.rag.embeddings import MockEmbeddingGenerator
from app.services.rag_service import RAGService
from app.schemas.document import DocumentIngestRequest

def test_document_chunking_and_hashing():
    chunker = TextChunker(chunk_size=300, chunk_overlap=50)
    raw_text = "Paragraph 1 with financial performance.\n\nParagraph 2 with debt reduction details.\n\nParagraph 3 with risk disclosures."
    chunks = chunker.chunk_document(raw_text, "doc-123", "Filings")
    assert len(chunks) >= 1
    for c in chunks:
        assert "content_hash" in c
        assert len(c["content_hash"]) == 64  # SHA-256 hex length
        assert c["page_number"] >= 1

def test_mock_embeddings_deterministic():
    gen = MockEmbeddingGenerator(dim=1536)
    v1 = gen.generate_query_embedding("Renewable wind generation in Tamil Nadu")
    v2 = gen.generate_query_embedding("Renewable wind generation in Tamil Nadu")
    assert len(v1) == 1536
    assert v1 == v2  # strictly deterministic

def test_rag_service_retrieval(db_session):
    mock_gen = MockEmbeddingGenerator(dim=1536)
    rag = RAGService(db_session, embedding_generator=mock_gen)
    results = rag.retrieve_evidence("Orient Green Power wind installed capacity", symbol_hint="GREENPOWER")
    assert len(results) > 0
    top = results[0]
    assert "Orient Green Power" in top.document_title or "Orient Green Power" in top.content
    assert top.content_hash is not None
    assert top.source_url_or_identifier is not None
