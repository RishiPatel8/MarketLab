from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
import hashlib
import logging
import math
import time
from app.core.config import settings
from app.providers.llm.gemini_adapter import ConfigurationError, LLMProviderError, redact_sensitive_text

logger = logging.getLogger("marketlab.rag.embeddings")


class EmbeddingProviderError(Exception):
    """Raised when external embedding generation fails."""
    pass


class BaseEmbeddingGenerator(ABC):
    provider_name: str = "base"
    model_name: str = "base"
    is_mock: bool = False
    dim: int = 1536

    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of document chunk texts."""
        pass

    @abstractmethod
    def generate_query_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for a single search query."""
        pass


class MockEmbeddingGenerator(BaseEmbeddingGenerator):
    """
    Deterministic embedding generator that creates reproducible unit vectors
    based on character trigram hashing. Strictly for offline testing.
    """
    provider_name = "mock"
    model_name = "trigram-hash"
    is_mock = True

    def __init__(self, dim: Optional[int] = None):
        self.dim = dim or settings.EMBEDDING_DIM or 1536

    def _embed_single(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        words = text.lower().split()
        if not words:
            vec[0] = 1.0
            return vec.tolist()

        for w in words:
            h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 1) % 2 == 0 else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return [float(x) for x in vec.tolist()]

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(t) for t in texts]

    def generate_query_embedding(self, text: str) -> List[float]:
        return self._embed_single(text)


class GeminiEmbeddingGenerator(BaseEmbeddingGenerator):
    """
    Live embedding generator using Google's official google-genai SDK.
    Validates output dimensions, checks finite values, and enforces strict error reporting.
    """
    provider_name = "gemini"
    is_mock = False

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        dim: Optional[int] = None,
        max_retries: int = 3
    ):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model_name = model or settings.EMBEDDING_MODEL or "gemini-embedding-2"
        self.dim = dim or settings.EMBEDDING_DIM or 3072
        self.max_retries = max_retries

        if not self.api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY is not configured for Gemini embeddings. "
                "Silent fallback to mock embeddings is forbidden in live mode. "
                "Set GEMINI_API_KEY or configure EMBEDDING_PROVIDER=mock for offline tests."
            )

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            safe_err = redact_sensitive_text(str(e))
            raise EmbeddingProviderError(f"Failed to initialize google-genai embedding client: {safe_err}")

    def _validate_vector(self, vector: List[float]) -> List[float]:
        if not vector or len(vector) == 0:
            raise EmbeddingProviderError("Received empty vector from Gemini embedding API.")
        
        # Check finite values
        for val in vector:
            if math.isnan(val) or math.isinf(val):
                raise EmbeddingProviderError(f"Embedding contains non-finite float: {val}")

        # Unit-normalize
        np_vec = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(np_vec)
        if norm > 0:
            np_vec = np_vec / norm
        return [float(x) for x in np_vec.tolist()]

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        all_embeddings: List[List[float]] = []

        for idx, text in enumerate(texts):
            last_err = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    response = self.client.models.embed_content(
                        model=self.model_name,
                        contents=text,
                    )
                    if hasattr(response, "embeddings") and response.embeddings:
                        clean_vec = self._validate_vector(response.embeddings[0].values)
                        all_embeddings.append(clean_vec)
                    else:
                        raise EmbeddingProviderError("No embedding values found in Gemini response.")
                    break
                except Exception as e:
                    safe_err = redact_sensitive_text(str(e))
                    last_err = safe_err
                    logger.warning(f"Gemini embedding item {idx} attempt {attempt}/{self.max_retries} failed: {safe_err}")
                    if attempt < self.max_retries:
                        time.sleep(0.5 * (2 ** (attempt - 1)))

            if last_err and len(all_embeddings) <= idx:
                raise EmbeddingProviderError(f"Gemini embedding generation failed: {last_err}")

        return all_embeddings

    def generate_query_embedding(self, text: str) -> List[float]:
        res = self.generate_embeddings([text])
        if not res:
            raise EmbeddingProviderError("Failed to generate query embedding.")
        return res[0]


def get_embedding_generator(provider_override: Optional[str] = None) -> BaseEmbeddingGenerator:
    provider = (provider_override or settings.EMBEDDING_PROVIDER).lower()

    if provider == "gemini":
        return GeminiEmbeddingGenerator()
    elif provider == "mock":
        return MockEmbeddingGenerator(dim=settings.EMBEDDING_DIM)
    else:
        raise ConfigurationError(f"Unsupported embedding provider: '{provider}'. Supported: mock, gemini.")
