"""Vector search over stored chunk embeddings.

The default store searches embeddings held in SQLite (loaded into a numpy
matrix), which is plenty for tens of thousands of chunks with zero extra
infrastructure. The ``VectorStore`` interface exists so alternative backends
(Qdrant, Weaviate, Redis, pgvector, FAISS) can be added — see the "good first
issue" list in the README.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from .db import Database


@dataclass
class SearchHit:
    chunk_id: str
    document_id: str
    text: str
    score: float


class VectorStore(ABC):
    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int) -> list[SearchHit]:
        """Return the ``top_k`` most similar chunks by cosine similarity."""


class SqliteVectorStore(VectorStore):
    """Brute-force cosine search over embeddings stored in the SQLite database.

    Embeddings are L2-normalized at write time, so cosine similarity reduces
    to a dot product.
    """

    def __init__(self, db: Database) -> None:
        self._db = db

    def search(self, query_vector: np.ndarray, top_k: int) -> list[SearchHit]:
        chunks, matrix = self._db.all_embeddings()
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
                text=chunks[i].text,
                score=float(scores[i]),
            )
            for i in top_indices
        ]
