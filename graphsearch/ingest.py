"""CLI for bulk-ingesting documents (text, Markdown, PDF) from a directory.

Usage:
    graphsearch-ingest data/example_docs
    graphsearch-ingest report.pdf
    python -m graphsearch.ingest data/example_docs
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import get_settings
from .extract import SUPPORTED_SUFFIXES, extract_text
from .rag import RagService


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
    exit_code = 0
    try:
        for path in files:
            try:
                content = extract_text(path.name, path.read_bytes())
                record = service.ingest(content, title=path.stem, source=str(path))
                print(f"ingested {path} -> {record.id} ({record.chunk_count} chunks)")
            except ValueError as exc:
                print(f"skipped {path}: {exc}", file=sys.stderr)
                exit_code = 1
    finally:
        service.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
