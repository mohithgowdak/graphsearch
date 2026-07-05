"""Tests for the sentence-transformers backend.

Skipped when the 'local' extra is not installed (e.g. in CI) — the model
download and torch dependency are too heavy for the default test matrix.
"""

import numpy as np
import pytest

pytest.importorskip("sentence_transformers")

from graphsearch.embeddings import LocalEmbedder  # noqa: E402


@pytest.fixture(scope="module")
def embedder() -> LocalEmbedder:
    return LocalEmbedder()


def test_embeddings_are_normalized(embedder):
    vectors = embedder.embed(["hello world"])
    assert vectors.shape == (1, embedder.dimension)
    assert abs(np.linalg.norm(vectors[0]) - 1.0) < 1e-3


def test_semantic_similarity_beats_lexical(embedder):
    """Paraphrases with no shared keywords must outscore unrelated text."""
    query, paraphrase, unrelated = embedder.embed(
        [
            "How do I get my money back?",
            "Refunds are issued to the original payment method.",
            "The weather in Tokyo is sunny today.",
        ]
    )
    assert float(query @ paraphrase) > float(query @ unrelated)
