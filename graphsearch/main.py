"""FastAPI application entrypoint.

Routes:
- ``/``        — the Playground UI: test ingestion and Q&A with your own docs
- ``/graphql`` — the GraphQL endpoint, with GraphiQL enabled
- ``/health``  — liveness probe
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from importlib import resources

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

    playground_html = (
        resources.files("graphsearch").joinpath("static/index.html").read_text(encoding="utf-8")
    )

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def playground() -> str:
        return playground_html

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
