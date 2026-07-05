import pytest

from graphsearch.extract import SUPPORTED_SUFFIXES, extract_text
from tests.pdf_fixture import make_pdf


def test_plain_text_is_decoded():
    assert extract_text("notes.txt", b"hello world") == "hello world"


def test_utf8_bom_is_stripped():
    assert extract_text("notes.md", b"\xef\xbb\xbfhello") == "hello"


def test_pdf_text_is_extracted():
    pdf = make_pdf("Refunds are issued within 30 days.")
    assert extract_text("policy.pdf", pdf) == "Refunds are issued within 30 days."


def test_pdf_without_text_raises_helpful_error():
    pdf = make_pdf("")
    with pytest.raises(ValueError, match="OCR"):
        extract_text("scan.pdf", pdf)


def test_pdf_suffix_is_supported():
    assert ".pdf" in SUPPORTED_SUFFIXES


def test_ingest_pipeline_accepts_pdf(service):
    content = extract_text("faq.pdf", make_pdf("The API rate limit is 100 requests per minute."))
    service.ingest(content, title="faq")
    hits = service.search("what is the rate limit", top_k=1)
    assert "100 requests" in hits[0].text
