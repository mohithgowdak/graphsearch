"""Split documents into overlapping chunks suitable for embedding."""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split ``text`` into chunks of at most ``chunk_size`` characters.

    Prefers paragraph boundaries, then falls back to a sliding window with
    ``overlap`` characters of context carried between adjacent chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(para) <= chunk_size:
            current = para
        else:
            # Paragraph alone exceeds chunk_size: sliding window.
            step = chunk_size - overlap
            for start in range(0, len(para), step):
                piece = para[start : start + chunk_size]
                if len(piece) < overlap and chunks:
                    # Tiny tail already covered by the previous window's overlap.
                    break
                chunks.append(piece)
            current = ""
    if current:
        chunks.append(current)
    return chunks
