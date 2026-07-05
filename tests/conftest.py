from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from graphsearch.config import Settings
from graphsearch.main import create_app
from graphsearch.rag import RagService


@pytest.fixture()
def settings(tmp_path) -> Settings:
    return Settings(
        database_path=str(tmp_path / "test.db"),
        embeddings="hash",
        llm="extractive",
    )


@pytest.fixture()
def service(settings) -> RagService:
    svc = RagService(settings)
    yield svc
    svc.close()


@pytest.fixture()
def client(settings, service) -> TestClient:
    app = create_app(settings, rag_service=service)
    with TestClient(app) as test_client:
        yield test_client


def graphql(client: TestClient, query: str, variables: dict | None = None) -> dict:
    response = client.post("/graphql", json={"query": query, "variables": variables or {}})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "errors" not in payload, payload.get("errors")
    return payload["data"]
