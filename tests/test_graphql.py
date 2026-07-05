import json

from tests.conftest import graphql
from tests.pdf_fixture import make_pdf

UPLOAD = """
mutation Upload($content: String!, $title: String) {
  uploadDocument(content: $content, title: $title) {
    id
    title
    chunkCount
  }
}
"""

ANSWER = """
query Ask($question: String!) {
  answer(question: $question) {
    text
    sources { id documentId documentTitle text score }
  }
}
"""


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_playground_ui_is_served_at_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "GraphSearch Playground" in response.text


def test_upload_and_answer_roundtrip(client):
    data = graphql(
        client,
        UPLOAD,
        {"content": "To reset your password, go to Settings > Security.", "title": "faq"},
    )
    doc = data["uploadDocument"]
    assert doc["title"] == "faq"
    assert doc["chunkCount"] >= 1

    data = graphql(client, ANSWER, {"question": "How do I reset my password?"})
    answer = data["answer"]
    assert "password" in answer["text"]
    assert answer["sources"][0]["documentId"] == doc["id"]
    assert answer["sources"][0]["documentTitle"] == "faq"


def test_search_query(client):
    graphql(client, UPLOAD, {"content": "Invoices are emailed on the 1st of each month."})
    data = graphql(client, "query { search(query: \"when are invoices sent\") { text score } }")
    assert data["search"]
    assert "Invoices" in data["search"][0]["text"]


def test_documents_listing_and_delete(client):
    doc_id = graphql(client, UPLOAD, {"content": "Doc to delete."})["uploadDocument"]["id"]

    data = graphql(client, "query { documents { id } }")
    assert any(d["id"] == doc_id for d in data["documents"])

    data = graphql(
        client,
        "mutation Delete($id: ID!) { deleteDocument(id: $id) }",
        {"id": doc_id},
    )
    assert data["deleteDocument"] is True

    data = graphql(client, "query { documents { id } }")
    assert all(d["id"] != doc_id for d in data["documents"])


def test_document_by_id_returns_null_when_missing(client):
    data = graphql(client, 'query { document(id: "does-not-exist") { id } }')
    assert data["document"] is None


UPLOAD_FILE = """
mutation UploadFile($file: Upload!, $title: String) {
  uploadFile(file: $file, title: $title) { id title chunkCount }
}
"""


def _upload_file(client, filename, data, content_type):
    return client.post(
        "/graphql",
        data={
            "operations": json.dumps(
                {"query": UPLOAD_FILE, "variables": {"file": None, "title": None}}
            ),
            "map": json.dumps({"0": ["variables.file"]}),
        },
        files={"0": (filename, data, content_type)},
    )


def test_upload_pdf_file_and_query_it(client):
    pdf = make_pdf("The warranty period is two years from purchase.")
    response = _upload_file(client, "warranty.pdf", pdf, "application/pdf")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "errors" not in payload, payload.get("errors")
    doc = payload["data"]["uploadFile"]
    assert doc["title"] == "warranty"  # defaults to the filename stem
    assert doc["chunkCount"] >= 1

    data = graphql(client, "query { search(query: \"how long is the warranty\") { text } }")
    assert "two years" in data["search"][0]["text"]


def test_upload_text_file_via_multipart(client):
    response = _upload_file(client, "notes.md", b"# Team\n\nStandup is at 9:30.", "text/markdown")
    payload = response.json()
    assert "errors" not in payload, payload.get("errors")
    assert payload["data"]["uploadFile"]["title"] == "notes"


def test_empty_upload_returns_graphql_error(client):
    response = client.post(
        "/graphql",
        json={"query": UPLOAD, "variables": {"content": "   "}},
    )
    assert response.status_code == 200
    assert response.json()["errors"]
