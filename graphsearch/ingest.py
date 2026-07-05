"""CLI for bulk-ingesting documents from a directory.

Usage:
    graphsearch-ingest data/example_docs
    python -m graphsearch.ingest data/example_docs
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import get_settings
from .rag import RagService

SUPPORTED_SUFFIXES = {".txt", ".md", ".markdown", ".rst"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest text/markdown files into GraphSearch")
    parser.add_argument("path", type=Path, help="File or directory to ingest")
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"error: {args.path} does not exist", file=sys.stderr)
        return 1

    files = (
        [args.path]
        if args.path.is_file()
        else sorted(
            p for p in args.path.rglob("*") if p.suffix.lower() in SUPPORTED_SUFFIXES
        )
    )
    if not files:
        print(f"error: no ingestable files under {args.path}", file=sys.stderr)
        return 1

    service = RagService(get_settings())
    try:
        for path in files:
            content = path.read_text(encoding="utf-8")
            record = service.ingest(content, title=path.stem, source=str(path))
            print(f"ingested {path} -> {record.id} ({record.chunk_count} chunks)")
    finally:
        service.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
