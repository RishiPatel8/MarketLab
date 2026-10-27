from abc import ABC, abstractmethod
from typing import List
import numpy as np
import hashlib
from app.core.config import settings

class BaseEmbeddingGenerator(ABC):
    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def generate_query_embedding(self, text: str) -> List[float]:
        pass


class MockEmbeddingGenerator(BaseEmbeddingGenerator):
    """
    Deterministic embedding generator that creates reproducible 1536-dim unit vectors
    based on character trigram hashing. Works offline with 0 external API dependencies.
    """
    def __init__(self, dim: int = 1536):
        self.dim = dim

    def _embed_single(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        words = text.lower().split()
        if not words:
            vec[0] = 1.0
            return vec.tolist()

        for w in words:
            # Map word hash into vector indices
            h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 1) % 2 == 0 else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(t) for t in texts]

    def generate_query_embedding(self, text: str) -> List[float]:
        return self._embed_single(text)


def get_embedding_generator() -> BaseEmbeddingGenerator:
    # Future extensibility: connect to OpenAI / Gemini if configured
    return MockEmbeddingGenerator(dim=settings.EMBEDDING_DIM)
