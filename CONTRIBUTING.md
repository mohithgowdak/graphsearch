# Contributing to GraphSearch

Thanks for your interest in contributing! This document covers the essentials.

## Development setup

```bash
git clone https://github.com/mohithgowdak/graphsearch
cd graphsearch
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

Run the checks that CI runs:

```bash
ruff check .
pytest -v
```

Tests are fully offline — they use the `hash` embedder and `extractive` LLM
backends, so no API keys are needed.

## Adding a backend

The three pipeline interfaces live in:

- `graphsearch/embeddings.py` — subclass `Embedder`, implement `embed()`,
  register in `create_embedder()`.
- `graphsearch/vectorstore.py` — subclass `VectorStore`, implement `search()`.
- `graphsearch/llm.py` — subclass `LLM`, implement `generate()`,
  register in `create_llm()`.

Guidelines for backends:

- Keep provider SDKs as **optional dependencies** (add an extra in
  `pyproject.toml`) and import them lazily inside `__init__` with a helpful
  error message, following the existing OpenAI/Anthropic pattern.
- Add at least one test. If the backend needs a live service, mock the client;
  CI has no network access to providers.

## Pull requests

1. Fork and create a feature branch from `main`.
2. Keep PRs focused — one feature or fix per PR.
3. Add or update tests for any behavior change.
4. Make sure `ruff check .` and `pytest` pass.
5. Describe *what* and *why* in the PR body.

## Reporting issues

Use the issue tracker. Include your Python version, OS, configuration
(`GRAPHSEARCH_*` env vars, minus secrets), and steps to reproduce.

## Code of Conduct

By participating you agree to our [Code of Conduct](CODE_OF_CONDUCT.md).
