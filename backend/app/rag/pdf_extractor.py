from typing import Dict, Any, List, Optional
import io
import hashlib
import logging
from datetime import datetime, timezone

logger = logging.getLogger("marketlab.rag.pdf_extractor")


class PDFExtractionResult:
    def __init__(
        self,
        text: str,
        page_count: int,
        pages_text: List[Dict[str, Any]],
        content_hash: str,
        file_size_bytes: int,
        status: str = "success",
        error_message: Optional[str] = None
    ):
        self.text = text
        self.page_count = page_count
        self.pages_text = pages_text
        self.content_hash = content_hash
        self.file_size_bytes = file_size_bytes
        self.status = status
        self.error_message = error_message


class PDFDocumentExtractor:
    """
    Robust PDF document extractor using pypdf.
    Computes cryptographic SHA-256 content hashes, parses page-level text,
    sanitizes content against injection attacks, and reports extraction status.
    """

    @staticmethod
    def extract_from_bytes(pdf_bytes: bytes, filename: str = "document.pdf") -> PDFExtractionResult:
        content_hash = hashlib.sha256(pdf_bytes).hexdigest()
        file_size = len(pdf_bytes)

        if not pdf_bytes:
            return PDFExtractionResult(
                text="",
                page_count=0,
                pages_text=[],
                content_hash=content_hash,
                file_size_bytes=0,
                status="empty_file",
                error_message="Uploaded PDF file contains 0 bytes."
            )

        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(reader.pages)
            pages_data: List[Dict[str, Any]] = []
            extracted_full_text: List[str] = []

            for page_idx, page in enumerate(reader.pages):
                page_num = page_idx + 1
                page_text = page.extract_text() or ""
                # Neutralize potential prompt injection tokens
                sanitized_text = page_text.replace("SYSTEM:", "[QUOTE: SYSTEM]").replace("Human:", "[QUOTE: Human]")
                pages_data.append({
                    "page_number": page_num,
                    "text": sanitized_text.strip(),
                    "char_count": len(sanitized_text)
                })
                extracted_full_text.append(f"[Page {page_num}]\n{sanitized_text.strip()}")

            combined_text = "\n\n".join(extracted_full_text).strip()
            status = "success" if combined_text else "scanned_or_empty"

            return PDFExtractionResult(
                text=combined_text,
                page_count=total_pages,
                pages_text=pages_data,
                content_hash=content_hash,
                file_size_bytes=file_size,
                status=status,
                error_message="Document may be a scanned image without embedded text." if not combined_text else None
            )

        except Exception as e:
            logger.error(f"Failed to parse PDF {filename}: {e}")
            return PDFExtractionResult(
                text="",
                page_count=0,
                pages_text=[],
                content_hash=content_hash,
                file_size_bytes=file_size,
                status="extraction_error",
                error_message=str(e)
            )
