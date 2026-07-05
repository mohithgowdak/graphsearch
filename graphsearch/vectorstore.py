"""Vector search over stored chunk embeddings.

The default store keeps an in-memory copy of the embedding matrix (loaded
from SQLite on first search, refreshed after writes), which is plenty for
tens of thousands of chunks with zero extra infrastructure. The
``VectorStore`` interface exists so alternative backends (Qdrant, Weaviate,
Redis, pgvector, FAISS) can be added — see the "good first issue" list in
the README.
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from .db import ChunkRecord, Database


@dataclass
class SearchHit:
    chunk_id: str
    document_id: str
    document_title: str | None
    text: str
    score: float


class VectorStore(ABC):
    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int) -> list[SearchHit]:
        """Return the ``top_k`` most similar chunks by cosine similarity."""

    def invalidate(self) -> None:  # noqa: B027 — intentional no-op default
        """Called after documents are added or removed. Override if the store caches."""


class SqliteVectorStore(VectorStore):
    """Cosine search over embeddings stored in the SQLite database.

    The chunk list and embedding matrix are cached in memory so queries are a
    single numpy matrix-vector product; ``invalidate()`` (called by
    ``RagService`` after ingest/delete) forces a reload on the next search.
    Embeddings are L2-normalized at write time, so cosine similarity reduces
    to a dot product.
    """

    def __init__(self, db: Database) -> None:
        self._db = db
        self._lock = threading.Lock()
        self._chunks: list[ChunkRecord] | None = None
        self._matrix: np.ndarray | None = None

    def invalidate(self) -> None:
        with self._lock:
            self._chunks = None
            self._matrix = None

    def _load(self) -> tuple[list[ChunkRecord], np.ndarray]:
        with self._lock:
            if self._chunks is None or self._matrix is None:
                self._chunks, self._matrix = self._db.all_embeddings()
            return self._chunks, self._matrix

    def search(self, query_vector: np.ndarray, top_k: int) -> list[SearchHit]:
        chunks, matrix = self._load()
        if not chunks:
            return []
        query = np.asarray(query_vector, dtype=np.float32).reshape(-1)
        scores = matrix @ query
        top_k = min(top_k, len(chunks))
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            SearchHit(
                chunk_id=chunks[i].id,
                document_id=chunks[i].document_id,
                document_title=chunks[i].document_title,
                text=chunks[i].text,
                score=float(scores[i]),
            )
            for i in top_indices
        ]
