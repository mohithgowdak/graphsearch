import pytest

from graphsearch.chunking import chunk_text


def test_empty_text_gives_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n\n  ") == []


def test_short_text_is_single_chunk():
    assert chunk_text("hello world") == ["hello world"]


def test_paragraphs_are_grouped_within_chunk_size():
    text = "para one\n\npara two\n\npara three"
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    assert all(len(c) <= 50 for c in chunks)
    joined = " ".join(chunks)
    for fragment in ("para one", "para two", "para three"):
        assert fragment in joined


def test_long_paragraph_is_windowed_with_overlap():
    text = "x" * 2000
    chunks = chunk_text(text, chunk_size=800, overlap=100)
    assert all(len(c) <= 800 for c in chunks)
    assert sum(len(c) for c in chunks) >= 2000  # overlap duplicates some content


def test_invalid_params_raise():
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=10, overlap=10)
