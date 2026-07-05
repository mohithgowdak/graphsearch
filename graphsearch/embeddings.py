"""Embedding backends.

Two implementations ship out of the box:

- ``HashEmbedder`` — deterministic character n-gram hashing. No API key or
  network needed, so the demo, tests, and CI all run offline. Retrieval
  quality is lexical rather than semantic, but it exercises the exact same
  pipeline.
- ``LocalEmbedder`` — real semantic embeddings computed locally with
  sentence-transformers. No API key, runs on CPU; the model (~80 MB for the
  default all-MiniLM-L6-v2) is downloaded on first use.
- ``OpenAIEmbedder`` — semantic embeddings via the OpenAI API.

To add a new backend (e.g. Cohere, Voyage), subclass ``Embedder`` and
register it in ``create_embedder``.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod

import numpy as np

from .config import Settings


class Embedder(ABC):
    """Turns text into a fixed-size vector. Vectors must be L2-normalized."""

    dimension: int

    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray:
        """Return an array of shape ``(len(texts), self.dimension)``."""


class HashEmbedder(Embedder):
    """Offline embedding via hashed character n-grams (a 'hashing trick' TF vector)."""

    def __init__(self, dimension: int = 512, ngram: int = 3) -> None:
        self.dimension = dimension
        self.ngram = ngram

    def _embed_one(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dimension, dtype=np.float32)
        normalized = " ".join(text.lower().split())
        for i in range(max(len(normalized) - self.ngram + 1, 1)):
            gram = normalized[i : i + self.ngram]
            digest = hashlib.md5(gram.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "little") % self.dimension
            vec[bucket] += 1.0
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        return np.vstack([self._embed_one(t) for t in texts])


class LocalEmbedder(Embedder):
    """Semantic embeddings computed locally with sentence-transformers (no API key)."""

    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "The 'sentence-transformers' package is required for "
                "GRAPHSEARCH_EMBEDDINGS=local. "
                "Install it with: pip install graphsearch-rag[local]"
            ) from exc
        self._model = SentenceTransformer(model)
        # Renamed in newer sentence-transformers releases; support both.
        get_dim = getattr(
            self._model, "get_embedding_dimension", None
        ) or self._model.get_sentence_embedding_dimension
        self.dimension = get_dim()

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        matrix = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(matrix, dtype=np.float32)


class OpenAIEmbedder(Embedder):
    """Semantic embeddings via the OpenAI embeddings API."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "The 'openai' package is required for GRAPHSEARCH_EMBEDDINGS=openai. "
                "Install it with: pip install graphsearch-rag[openai]"
            ) from exc
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY must be set for GRAPHSEARCH_EMBEDDINGS=openai")
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self.dimension = 1536 if "small" in model or "ada" in model else 3072

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        response = self._client.embeddings.create(model=self._model, input=texts)
        matrix = np.asarray([item.embedding for item in response.data], dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return matrix / norms


def create_embedder(settings: Settings) -> Embedder:
    if settings.embeddings == "hash":
        return HashEmbedder()
    if settings.embeddings == "local":
        return LocalEmbedder(settings.local_embedding_model)
    if settings.embeddings == "openai":
        return OpenAIEmbedder(settings.openai_api_key, settings.openai_embedding_model)
    raise ValueError(f"Unknown embeddings backend: {settings.embeddings!r}")
