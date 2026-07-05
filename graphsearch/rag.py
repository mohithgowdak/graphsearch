"""The RAG pipeline: ingest documents, retrieve relevant chunks, generate answers."""

from __future__ import annotations

from dataclasses import dataclass

from .chunking import chunk_text
from .config import Settings
from .db import Database, DocumentRecord
from .embeddings import Embedder, create_embedder
from .llm import LLM, create_llm
from .vectorstore import SearchHit, SqliteVectorStore, VectorStore


@dataclass
class AnswerResult:
    text: str
    sources: list[SearchHit]


class RagService:
    """Ties together the database, embedder, vector store, and LLM."""

    def __init__(
        self,
        settings: Settings,
        db: Database | None = None,
        embedder: Embedder | None = None,
        vector_store: VectorStore | None = None,
        llm: LLM | None = None,
    ) -> None:
        self.settings = settings
        self.db = db or Database(settings.database_path)
        self.embedder = embedder or create_embedder(settings)
        self.vector_store = vector_store or SqliteVectorStore(self.db)
        self.llm = llm or create_llm(settings)

    def ingest(
        self, content: str, title: str | None = None, source: str | None = None
    ) -> DocumentRecord:
        """Chunk, embed, and store a document."""
        chunks = chunk_text(content, self.settings.chunk_size, self.settings.chunk_overlap)
        if not chunks:
            raise ValueError("Document content is empty")
        embeddings = self.embedder.embed(chunks)
        record = self.db.insert_document(content, title, source, chunks, embeddings)
        self.vector_store.invalidate()
        return record

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and drop its chunks from the search index."""
        deleted = self.db.delete_document(doc_id)
        if deleted:
            self.vector_store.invalidate()
        return deleted

    def search(self, query: str, top_k: int | None = None) -> list[SearchHit]:
        """Embed the query and return the most similar chunks."""
        top_k = top_k or self.settings.default_top_k
        query_vector = self.embedder.embed([query])[0]
        return self.vector_store.search(query_vector, top_k)

    def answer(self, question: str, top_k: int | None = None) -> AnswerResult:
        """Retrieve relevant chunks and generate a grounded answer.

        Citation numbers in the answer text ([1], [2], …) refer to positions
        in ``sources`` (1-indexed).
        """
        hits = self.search(question, top_k)
        text = self.llm.generate(question, hits)
        return AnswerResult(text=text, sources=hits)

    def close(self) -> None:
        self.db.close()
