"""Strawberry GraphQL schema: types, queries, and mutations.

Field names are camelCased by Strawberry, so the public API matches the
project spec: ``answer(question:)``, ``uploadDocument(content:)``, etc.
Resolvers delegate to ``RagService`` via ``asyncio.to_thread`` so blocking
I/O (SQLite, provider APIs) never stalls the event loop.
"""

from __future__ import annotations

import asyncio

import strawberry
from strawberry.types import Info

from .db import DocumentRecord
from .rag import RagService
from .vectorstore import SearchHit


@strawberry.type
class Document:
    id: strawberry.ID
    title: str | None
    source: str | None
    content: str
    created_at: str
    chunk_count: int

    @staticmethod
    def from_record(record: DocumentRecord) -> Document:
        return Document(
            id=strawberry.ID(record.id),
            title=record.title,
            source=record.source,
            content=record.content,
            created_at=record.created_at,
            chunk_count=record.chunk_count,
        )


@strawberry.type
class Chunk:
    id: strawberry.ID
    document_id: strawberry.ID
    document_title: str | None
    text: str
    score: float

    @staticmethod
    def from_hit(hit: SearchHit) -> Chunk:
        return Chunk(
            id=strawberry.ID(hit.chunk_id),
            document_id=strawberry.ID(hit.document_id),
            document_title=hit.document_title,
            text=hit.text,
            score=hit.score,
        )


@strawberry.type
class Answer:
    text: str
    sources: list[Chunk] = strawberry.field(
        description="Retrieved passages; citations like [1] in `text` are 1-indexed into this list."
    )


def _service(info: Info) -> RagService:
    return info.context["rag_service"]


@strawberry.type
class Query:
    @strawberry.field(description="Ask a question and get an answer grounded in your documents.")
    async def answer(self, info: Info, question: str, top_k: int | None = None) -> Answer:
        result = await asyncio.to_thread(_service(info).answer, question, top_k)
        return Answer(text=result.text, sources=[Chunk.from_hit(h) for h in result.sources])

    @strawberry.field(description="Semantic search: return the most relevant chunks for a query.")
    async def search(self, info: Info, query: str, top_k: int | None = None) -> list[Chunk]:
        hits = await asyncio.to_thread(_service(info).search, query, top_k)
        return [Chunk.from_hit(h) for h in hits]

    @strawberry.field(description="List ingested documents, newest first.")
    async def documents(self, info: Info, limit: int = 20, offset: int = 0) -> list[Document]:
        records = await asyncio.to_thread(_service(info).db.list_documents, limit, offset)
        return [Document.from_record(r) for r in records]

    @strawberry.field(description="Fetch a single document by ID.")
    async def document(self, info: Info, id: strawberry.ID) -> Document | None:
        record = await asyncio.to_thread(_service(info).db.get_document, str(id))
        return Document.from_record(record) if record else None


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Ingest a document: it is chunked, embedded, and indexed.")
    async def upload_document(
        self,
        info: Info,
        content: str,
        title: str | None = None,
        source: str | None = None,
    ) -> Document:
        record = await asyncio.to_thread(_service(info).ingest, content, title, source)
        return Document.from_record(record)

    @strawberry.mutation(description="Delete a document and its indexed chunks.")
    async def delete_document(self, info: Info, id: strawberry.ID) -> bool:
        return await asyncio.to_thread(_service(info).delete_document, str(id))


schema = strawberry.Schema(query=Query, mutation=Mutation)
