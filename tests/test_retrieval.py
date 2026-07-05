import numpy as np

from graphsearch.embeddings import HashEmbedder


def test_hash_embedder_is_deterministic_and_normalized():
    embedder = HashEmbedder()
    a = embedder.embed(["the cat sat on the mat"])
    b = embedder.embed(["the cat sat on the mat"])
    np.testing.assert_array_equal(a, b)
    assert abs(np.linalg.norm(a[0]) - 1.0) < 1e-5


def test_similar_texts_score_higher_than_unrelated():
    embedder = HashEmbedder()
    query, similar, unrelated = embedder.embed(
        [
            "how do I reset my password",
            "to reset your password visit the account settings page",
            "the quarterly revenue grew by twelve percent in Q3",
        ]
    )
    assert float(query @ similar) > float(query @ unrelated)


def test_ingest_and_search_returns_relevant_chunk(service):
    service.ingest("To reset your password, go to Settings > Security.", title="passwords")
    service.ingest("Our refund policy allows returns within 30 days.", title="refunds")

    hits = service.search("how do I reset my password", top_k=1)
    assert len(hits) == 1
    assert "password" in hits[0].text


def test_answer_includes_sources(service):
    service.ingest("The support email is help@example.com.", title="support")
    result = service.answer("what is the support email?")
    assert result.sources
    assert "help@example.com" in result.text  # extractive mode echoes the top passage


def test_delete_document_removes_chunks_from_search(service):
    record = service.ingest("Kubernetes clusters are configured via kubeconfig.", title="k8s")
    assert service.search("kubernetes", top_k=5)
    assert service.db.delete_document(record.id)
    assert service.search("kubernetes", top_k=5) == []
