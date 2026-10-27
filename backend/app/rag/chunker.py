from typing import List, Dict, Any, Optional
import re
import hashlib

class TextChunker:
    """
    Splits financial documents into semantically coherent chunks,
    preserving section headers and paragraph boundaries where possible.
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        text: str,
        document_id: str,
        section_hint: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        cleaned_text = re.sub(r"\r\n", "\n", text).strip()
        paragraphs = re.split(r"\n\s*\n", cleaned_text)
        
        chunks: List[Dict[str, Any]] = []
        current_chunk_paragraphs = []
        current_len = 0
        chunk_idx = 0

        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue

            p_len = len(p_clean)
            if current_len + p_len > self.chunk_size and current_chunk_paragraphs:
                chunk_text = "\n\n".join(current_chunk_paragraphs)
                chunks.append({
                    "chunk_index": chunk_idx,
                    "content": chunk_text,
                    "section": section_hint or "General",
                    "page_number": (chunk_idx // 3) + 1,
                    "content_hash": hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
                })
                chunk_idx += 1
                # Retain overlap from previous
                current_chunk_paragraphs = [current_chunk_paragraphs[-1]] if self.chunk_overlap > 0 else []
                current_len = len(current_chunk_paragraphs[0]) if current_chunk_paragraphs else 0

            current_chunk_paragraphs.append(p_clean)
            current_len += p_len

        if current_chunk_paragraphs:
            chunk_text = "\n\n".join(current_chunk_paragraphs)
            chunks.append({
                "chunk_index": chunk_idx,
                "content": chunk_text,
                "section": section_hint or "General",
                "page_number": (chunk_idx // 3) + 1,
                "content_hash": hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
            })

        return chunks
