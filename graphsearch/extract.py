"""Extract plain text from uploaded files.

Text formats (.txt, .md, .markdown, .rst) are decoded as UTF-8; PDFs are
parsed with pypdf. To support a new format (docx, html, epub), add a branch
in ``extract_text``.
"""

from __future__ import annotations

import io
from pathlib import Path

TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".rst"}
PDF_SUFFIXES = {".pdf"}
SUPPORTED_SUFFIXES = TEXT_SUFFIXES | PDF_SUFFIXES


def extract_text(filename: str, data: bytes) -> str:
    """Return the plain text content of ``data``, dispatching on file extension."""
    suffix = Path(filename).suffix.lower()
    if suffix in PDF_SUFFIXES:
        return _extract_pdf(data)
    # Default: treat as UTF-8 text ("utf-8-sig" strips a BOM if present).
    return data.decode("utf-8-sig", errors="replace")


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    if reader.is_encrypted:
        raise ValueError("PDF is password-protected; decrypt it before uploading")
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(part.strip() for part in pages if part.strip())
    if not text:
        raise ValueError(
            "No extractable text found in PDF — it may be scanned images. "
            "Run OCR on it first (e.g. ocrmypdf), then upload the result."
        )
    return text
