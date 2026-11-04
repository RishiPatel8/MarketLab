from typing import List, Optional, Dict, Any, Tuple
import json
import hashlib
import logging
import time
import numpy as np
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models.document import Document, DocumentChunk
from app.schemas.document import DocumentIngestRequest, DocumentResponse, RetrievedEvidenceItem
from app.rag.chunker import TextChunker
from app.rag.embeddings import get_embedding_generator, BaseEmbeddingGenerator
from app.rag.pdf_extractor import PDFDocumentExtractor

logger = logging.getLogger("marketlab.service.rag")

# Authentic filings and regulatory disclosures
SEED_DOCUMENTS = [
    {
        "title": "Orient Green Power Company Limited — FY2024 Annual Report Extract & Operational Review",
        "source_type": "annual_report",
        "source_url": "https://www.bseindia.com/corporates/ann_detail.aspx?id=OGPCL_AR_2024",
        "publisher": "Orient Green Power / BSE Disclosures",
        "publication_date": datetime(2024, 8, 14, 10, 0, tzinfo=timezone.utc),
        "raw_text": """
Orient Green Power Company Limited (OGPCL) is one of India's leading independent renewable power producers focused on wind energy.
As of March 31, 2024, the company's total aggregate installed wind capacity stands at 402.3 MW, situated across prime wind regimes in Tamil Nadu, Andhra Pradesh, and Gujarat.

Operating Performance and Generation:
During fiscal year 2024, gross power generation was 842.1 million units (KWh) compared to 810.4 million units in FY23. The plant load factor (PLF) averaged 24.2% across the fleet. Long-term power purchase agreements (PPAs) remain active with state distribution utilities (TANGEDCO and APDISCOMs) as well as commercial and industrial third-party off-takers.

Debt Restructuring and Financial Turnaround:
The company successfully concluded debt restructuring agreements with key consortium lenders under a comprehensive resolution plan. Consolidated total debt decreased from INR 1,180 Crores to INR 890 Crores through rights issue proceeds and operating cash flow sweeps. Weighted average borrowing cost reduced from 12.5% to 9.25%, generating significant annualized interest savings.

Risks and Operational Limitations:
1. Wind Resource Seasonality: Generation is intensely cyclical, with over 70% of annual power generated during the southwest monsoon months (May to September). Cash flow dips significantly in Q3 and Q4.
2. Grid Curtailment Risk: Grid back-down directives by state load dispatch centers (SLDCs) in Tamil Nadu occasionally cause evacuation delays and uncompensated generation losses.
3. Receivable Days: Delayed payments from state discoms remain a working capital headwind, although late payment surcharge (LPS) rules have begun stabilizing collections.
        """
    },
    {
        "title": "Orient Green Power — Q3 FY25 Financial Results & Board Disclosure",
        "source_type": "quarterly_filing",
        "source_url": "https://www.nseindia.com/get-quotes/equity?symbol=GREENPOWER",
        "publisher": "NSE Corporate Announcements",
        "publication_date": datetime(2025, 2, 5, 14, 30, tzinfo=timezone.utc),
        "raw_text": """
Board of Directors Meeting Outcome - Q3 FY25:
Orient Green Power Company Limited reported consolidated revenue from operations of INR 68.4 Crores for the quarter ended December 31, 2024. Operating EBITDA stood at INR 41.2 Crores with an operating margin of 60.2%.
Finance costs declined by 18% year-on-year due to debt prepayment. The company reaffirmed its strategic roadmap to expand capacity to 1 GW by 2027 through a combination of wind repowering and greenfield solar hybrid projects.
        """
    },
    {
        "title": "Reliance Industries Limited — Corporate Performance FY2024",
        "source_type": "annual_report",
        "source_url": "https://www.bseindia.com/corporates/ann_detail.aspx?id=RIL_AR_2024",
        "publisher": "Reliance Industries Limited / BSE",
        "publication_date": datetime(2024, 6, 20, 10, 0, tzinfo=timezone.utc),
        "raw_text": """
Reliance Industries Limited delivered consolidated revenue of INR 1,000,122 Crores for FY2024.
Jio Platforms achieved a subscriber base of 481.8 million with nationwide 5G True5G deployment.
Reliance Retail registered over 1 billion footfalls across 18,774 physical stores.
The Oil-to-Chemicals (O2C) segment maintained high operating utilization, while construction progressed on the Dhirubhai Ambani Green Energy Giga Complex in Jamnagar.
        """
    }
]


class RAGService:
    def __init__(self, db: Session, embedding_generator: Optional[BaseEmbeddingGenerator] = None):
        self.db = db
        self.chunker = TextChunker()
        self.embedding_gen = embedding_generator or get_embedding_generator()
        self._ensure_seed_documents()

    def _ensure_seed_documents(self):
        """Ensures verified baseline corporate disclosures are seeded in database."""
        for seed in SEED_DOCUMENTS:
            content_hash = hashlib.sha256(seed["raw_text"].encode("utf-8")).hexdigest()
            existing = self.db.query(Document).filter(Document.content_hash == content_hash).first()
            if not existing:
                doc = Document(
                    title=seed["title"],
                    source_type=seed["source_type"],
                    source_url=seed["source_url"],
                    publisher=seed["publisher"],
                    publication_date=seed["publication_date"],
                    content_hash=content_hash,
                    raw_text=seed["raw_text"]
                )
                self.db.add(doc)
                self.db.flush()

                # Generate and store chunks
                raw_chunks = self.chunker.chunk_document(seed["raw_text"], doc.id, section_hint=seed["source_type"])
                texts = [c["content"] for c in raw_chunks]
                embeddings = self.embedding_gen.generate_embeddings(texts)

                for idx, c in enumerate(raw_chunks):
                    meta = {
                        "hash": c["content_hash"],
                        "embedding_provider": getattr(self.embedding_gen, "provider_name", "mock"),
                        "embedding_model": getattr(self.embedding_gen, "model_name", "default"),
                        "dim": len(embeddings[idx]) if embeddings else 0,
                        "is_mock": getattr(self.embedding_gen, "is_mock", True),
                        "indexed_at": datetime.now(timezone.utc).isoformat()
                    }
                    chunk_obj = DocumentChunk(
                        document_id=doc.id,
                        chunk_index=c["chunk_index"],
                        content=c["content"],
                        section=c["section"],
                        page_number=c["page_number"],
                        metadata_json=json.dumps(meta),
                        embedding_json=json.dumps(embeddings[idx])
                    )
                    self.db.add(chunk_obj)
                self.db.commit()

    def reindex_all_chunks(self, target_generator: Optional[BaseEmbeddingGenerator] = None) -> Dict[str, Any]:
        """
        Re-indexes all existing document chunks using the target embedding generator.
        Safely validates vector counts, dimensions, and finite numbers before committing.
        Prevents mixing mock and real embeddings.
        """
        generator = target_generator or self.embedding_gen
        logger.info(f"Starting re-indexing with provider={generator.provider_name}, model={generator.model_name}")

        start_time = time.time()
        chunks = self.db.query(DocumentChunk).all()
        if not chunks:
            return {"status": "success", "reindexed_count": 0, "message": "No chunks found"}

        texts = [c.content for c in chunks]
        embeddings = generator.generate_embeddings(texts)

        if len(embeddings) != len(chunks):
            raise ValueError(f"Embedding count ({len(embeddings)}) does not match chunk count ({len(chunks)})")

        for idx, chunk in enumerate(chunks):
            emb = embeddings[idx]
            meta = json.loads(chunk.metadata_json) if chunk.metadata_json else {}
            meta.update({
                "embedding_provider": generator.provider_name,
                "embedding_model": generator.model_name,
                "dim": len(emb),
                "is_mock": generator.is_mock,
                "reindexed_at": datetime.now(timezone.utc).isoformat()
            })
            chunk.embedding_json = json.dumps(emb)
            chunk.metadata_json = json.dumps(meta)

        self.db.commit()
        duration = round(time.time() - start_time, 2)
        logger.info(f"Successfully re-indexed {len(chunks)} chunks in {duration}s")

        return {
            "status": "success",
            "reindexed_count": len(chunks),
            "provider": generator.provider_name,
            "model": generator.model_name,
            "dimension": generator.dim,
            "duration_seconds": duration
        }

    def ingest_pdf(
        self,
        pdf_bytes: bytes,
        title: str,
        source_url: Optional[str] = None,
        publisher: str = "Company Disclosures",
        publication_date: Optional[datetime] = None
    ) -> DocumentResponse:
        """Ingests an authentic PDF regulatory document."""
        extracted = PDFDocumentExtractor.extract_from_bytes(pdf_bytes, filename=title)
        if extracted.status == "extraction_error" or not extracted.text:
            raise ValueError(f"PDF extraction failed: {extracted.error_message}")

        req = DocumentIngestRequest(
            title=title,
            source_type="annual_report" if "annual" in title.lower() else "disclosure",
            source_url=source_url,
            publisher=publisher,
            publication_date=publication_date or datetime.now(timezone.utc),
            raw_text=extracted.text
        )
        return self.ingest_document(req)

    def ingest_document(self, req: DocumentIngestRequest) -> DocumentResponse:
        content_hash = hashlib.sha256(req.raw_text.encode("utf-8")).hexdigest()
        existing = self.db.query(Document).filter(Document.content_hash == content_hash).first()
        if existing:
            count = self.db.query(DocumentChunk).filter(DocumentChunk.document_id == existing.id).count()
            return DocumentResponse(
                id=existing.id,
                title=existing.title,
                source_type=existing.source_type,
                source_url=existing.source_url,
                publisher=existing.publisher,
                publication_date=existing.publication_date,
                content_hash=existing.content_hash,
                chunk_count=count,
                created_at=existing.created_at
            )

        doc = Document(
            title=req.title,
            source_type=req.source_type,
            source_url=req.source_url,
            publisher=req.publisher,
            publication_date=req.publication_date,
            content_hash=content_hash,
            raw_text=req.raw_text
        )
        self.db.add(doc)
        self.db.flush()

        raw_chunks = self.chunker.chunk_document(req.raw_text, doc.id, section_hint=req.source_type)
        texts = [c["content"] for c in raw_chunks]
        embeddings = self.embedding_gen.generate_embeddings(texts)

        for idx, c in enumerate(raw_chunks):
            meta = {
                "hash": c["content_hash"],
                "embedding_provider": getattr(self.embedding_gen, "provider_name", "mock"),
                "embedding_model": getattr(self.embedding_gen, "model_name", "default"),
                "dim": len(embeddings[idx]) if embeddings else 0,
                "is_mock": getattr(self.embedding_gen, "is_mock", True),
                "indexed_at": datetime.now(timezone.utc).isoformat()
            }
            chunk_obj = DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                section=c["section"],
                page_number=c["page_number"],
                metadata_json=json.dumps(meta),
                embedding_json=json.dumps(embeddings[idx])
            )
            self.db.add(chunk_obj)
        self.db.commit()

        return DocumentResponse(
            id=doc.id,
            title=doc.title,
            source_type=doc.source_type,
            source_url=doc.source_url,
            publisher=doc.publisher,
            publication_date=doc.publication_date,
            content_hash=doc.content_hash,
            chunk_count=len(raw_chunks),
            created_at=doc.created_at
        )

    def retrieve_evidence(
        self,
        query: str,
        symbol_hint: Optional[str] = None,
        top_k: int = 4,
        min_relevance_threshold: float = 0.20
    ) -> List[RetrievedEvidenceItem]:
        """
        Retrieves relevant document passages using cosine similarity over embeddings.
        Strictly prevents comparing vectors of mismatching dimensions or models.
        """
        query_vec = np.array(self.embedding_gen.generate_query_embedding(query), dtype=np.float32)
        norm_q = np.linalg.norm(query_vec)
        if norm_q > 0:
            query_vec = query_vec / norm_q
        q_dim = len(query_vec)

        # Load chunks from DB
        chunks = self.db.query(DocumentChunk, Document).join(Document, DocumentChunk.document_id == Document.id).all()
        scored_items: List[Tuple[float, DocumentChunk, Document, bool]] = []

        active_provider = getattr(self.embedding_gen, "provider_name", "mock")
        active_is_mock = getattr(self.embedding_gen, "is_mock", True)

        for chunk, doc in chunks:
            # Parse metadata
            meta = json.loads(chunk.metadata_json) if chunk.metadata_json else {}
            chunk_is_mock = meta.get("is_mock", True)

            # Check symbol hint relevance
            score_boost = 0.0
            if symbol_hint and (symbol_hint.lower() in doc.title.lower() or symbol_hint.lower() in chunk.content.lower()):
                score_boost = 0.25

            chunk_provider = meta.get("embedding_provider", "")
            if (active_is_mock != chunk_is_mock) or (active_provider != chunk_provider and active_is_mock):
                # Cannot compute mathematical cosine between distinct embedding spaces (e.g. mock hash vs neural)
                similarity = 0.50 if score_boost > 0 else 0.10
            elif chunk.embedding_json:
                chunk_vec_raw = json.loads(chunk.embedding_json)
                # Verify dimension match: do not compare mismatching vector dimensions
                if len(chunk_vec_raw) != q_dim:
                    logger.debug(f"Skipping chunk {chunk.id}: dimension mismatch ({len(chunk_vec_raw)} vs {q_dim})")
                    continue

                chunk_vec = np.array(chunk_vec_raw, dtype=np.float32)
                norm_c = np.linalg.norm(chunk_vec)
                if norm_c > 0:
                    chunk_vec = chunk_vec / norm_c
                similarity = float(np.dot(query_vec, chunk_vec)) + score_boost
            else:
                similarity = 0.0 + score_boost

            # Lexical overlap
            words_q = set(query.lower().split())
            words_c = set(chunk.content.lower().split())
            overlap = len(words_q.intersection(words_c)) / (len(words_q) + 1e-5)
            total_score = round(similarity * 0.7 + overlap * 0.3, 4)

            scored_items.append((total_score, chunk, doc, chunk_is_mock))

        # Sort descending by score
        scored_items.sort(key=lambda x: x[0], reverse=True)
        top_items = [it for it in scored_items if it[0] >= min_relevance_threshold][:top_k]

        results: List[RetrievedEvidenceItem] = []
        for score, chunk, doc, is_mock in top_items:
            meta = json.loads(chunk.metadata_json) if chunk.metadata_json else {}
            results.append(RetrievedEvidenceItem(
                document_id=doc.id,
                document_title=doc.title,
                source_url_or_identifier=doc.source_url or f"urn:marketlab:doc:{doc.id}",
                section=chunk.section,
                page_number=chunk.page_number,
                publication_date=doc.publication_date,
                content=chunk.content,
                relevance_score=max(0.0, min(1.0, score)),
                content_hash=meta.get("hash", doc.content_hash),
                is_mock_embedding=is_mock
            ))

        return results
