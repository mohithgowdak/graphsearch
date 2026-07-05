"""FastAPI application entrypoint. GraphQL is served at /graphql with GraphiQL enabled."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from . import __version__
from .config import Settings, get_settings
from .rag import RagService
from .schema import schema


def create_app(settings: Settings | None = None, rag_service: RagService | None = None) -> FastAPI:
    settings = settings or get_settings()
    service = rag_service or RagService(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        service.close()

    app = FastAPI(title="GraphSearch", version=__version__, lifespan=lifespan)

    async def get_context() -> dict:
        return {"rag_service": service}

    graphql_router: GraphQLRouter = GraphQLRouter(schema, context_getter=get_context)
    app.include_router(graphql_router, prefix="/graphql")

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "version": __version__}

    return app


def run() -> None:
    """Console entrypoint: ``graphsearch``."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
