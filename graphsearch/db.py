"""SQLite persistence for documents, chunks, and their embeddings.

A single SQLite file stores everything, which keeps the default deployment
zero-dependency. Embeddings are stored as float32 blobs on the ``chunks``
table and searched in memory with numpy (see ``vectorstore.py``).
"""

from __future__ import annotations

import sqlite3
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    title TEXT,
    source TEXT,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    idx INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding BLOB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id);
"""


@dataclass
class DocumentRecord:
    id: str
    title: str | None
    source: str | None
    content: str
    created_at: str
    chunk_count: int


@dataclass
class ChunkRecord:
    id: str
    document_id: str
    idx: int
    text: str
    document_title: str | None = None


class Database:
    """Thread-safe wrapper around a SQLite connection."""

    def __init__(self, path: str) -> None:
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        self._lock = threading.Lock()

    def close(self) -> None:
        self._conn.close()

    # -- documents ---------------------------------------------------------

    def insert_document(
        self,
        content: str,
        title: str | None,
        source: str | None,
        chunks: list[str],
        embeddings: np.ndarray,
    ) -> DocumentRecord:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        doc_id = uuid.uuid4().hex
        created_at = datetime.now(timezone.utc).isoformat()
        with self._lock, self._conn:
            self._conn.execute(
                "INSERT INTO documents (id, title, source, content, created_at)"
                " VALUES (?, ?, ?, ?, ?)",
                (doc_id, title, source, content, created_at),
            )
            self._conn.executemany(
                "INSERT INTO chunks (id, document_id, idx, text, embedding)"
                " VALUES (?, ?, ?, ?, ?)",
                [
                    (
                        uuid.uuid4().hex,
                        doc_id,
                        i,
                        chunk,
                        np.asarray(emb, dtype=np.float32).tobytes(),
                    )
                    for i, (chunk, emb) in enumerate(zip(chunks, embeddings, strict=True))
                ],
            )
        return DocumentRecord(doc_id, title, source, content, created_at, len(chunks))

    def get_document(self, doc_id: str) -> DocumentRecord | None:
        row = self._conn.execute(
            "SELECT d.id, d.title, d.source, d.content, d.created_at,"
            " (SELECT COUNT(*) FROM chunks c WHERE c.document_id = d.id)"
            " FROM documents d WHERE d.id = ?",
            (doc_id,),
        ).fetchone()
        return DocumentRecord(*row) if row else None

    def list_documents(self, limit: int = 20, offset: int = 0) -> list[DocumentRecord]:
        rows = self._conn.execute(
            "SELECT d.id, d.title, d.source, d.content, d.created_at,"
            " (SELECT COUNT(*) FROM chunks c WHERE c.document_id = d.id)"
            " FROM documents d ORDER BY d.created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [DocumentRecord(*row) for row in rows]

    def delete_document(self, doc_id: str) -> bool:
        with self._lock, self._conn:
            cursor = self._conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        return cursor.rowcount > 0

    # -- chunks / embeddings -------------------------------------------------

    def all_embeddings(self) -> tuple[list[ChunkRecord], np.ndarray]:
        """Return every chunk with its embedding matrix (rows align with chunks)."""
        rows = self._conn.execute(
            "SELECT c.id, c.document_id, c.idx, c.text, d.title, c.embedding"
            " FROM chunks c JOIN documents d ON d.id = c.document_id"
        ).fetchall()
        if not rows:
            return [], np.empty((0, 0), dtype=np.float32)
        records = [ChunkRecord(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        matrix = np.vstack([np.frombuffer(r[5], dtype=np.float32) for r in rows])
        return records, matrix
