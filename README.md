# GraphSearch

**A GraphQL API server for Retrieval-Augmented Generation (RAG) over your documents.**

Upload documents through a GraphQL mutation, then ask questions through a GraphQL query.
GraphSearch chunks and embeds your documents, retrieves the most relevant passages with
vector similarity search, and feeds them to an LLM to generate a grounded answer — all
behind a single, typed, introspectable GraphQL endpoint.

```graphql
query {
  answer(question: "How do I reset my password?") {
    text
    sources { documentId text score }
  }
}
```

## Why GraphQL for RAG?

- **One endpoint, typed schema** — clients ask for exactly the fields they need
  (answer text, source chunks, scores) instead of juggling REST routes.
- **Introspection & tooling for free** — GraphiQL, codegen'd TypeScript clients,
  and schema docs come with the ecosystem.
- **Composable** — `answer`, `search`, and document management live in one schema
  and can be combined in a single request.

## Quickstart

### Run locally (no API keys needed)

The default configuration is fully offline: a hashing-trick embedder plus an
extractive answer mode. It exercises the entire pipeline and is perfect for
kicking the tires, tests, and CI.

```bash
git clone https://github.com/mohithgowdak/graphsearch
cd graphsearch
pip install -e ".[dev]"

# Ingest the bundled example docs
graphsearch-ingest data/example_docs

# Start the server
graphsearch
```

Open **http://localhost:8000/graphql** for the GraphiQL playground and try:

```graphql
query {
  answer(question: "What is the return policy?") {
    text
    sources { text score }
  }
}
```

### Run with Docker

```bash
docker compose up --build
```

### Use real embeddings and an LLM

Set the backends and keys via environment variables (or a `.env` file — see
[.env.example](.env.example)):

```bash
export GRAPHSEARCH_EMBEDDINGS=openai      # semantic embeddings
export GRAPHSEARCH_LLM=anthropic          # generated answers via Claude
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
pip install -e ".[openai,anthropic]"
graphsearch
```

| Setting | Options | Default |
|---|---|---|
| `GRAPHSEARCH_EMBEDDINGS` | `hash` (offline), `openai` | `hash` |
| `GRAPHSEARCH_LLM` | `extractive` (offline), `openai`, `anthropic` | `extractive` |

> **Note:** documents are embedded at ingest time, so re-ingest after switching
> embedding backends.

## GraphQL API

### Queries

```graphql
answer(question: String!, topK: Int): Answer!      # RAG: retrieve + generate
search(query: String!, topK: Int): [Chunk!]!       # raw semantic search
documents(limit: Int = 20, offset: Int = 0): [Document!]!
document(id: ID!): Document
```

### Mutations

```graphql
uploadDocument(content: String!, title: String, source: String): Document!
deleteDocument(id: ID!): Boolean!
```

### Example: ingest and ask in one session

```graphql
mutation {
  uploadDocument(
    content: "Support hours are 9am-5pm PST, Monday through Friday."
    title: "support-hours"
  ) { id chunkCount }
}

query {
  answer(question: "When is support available?") {
    text
    sources { documentId score }
  }
}
```

## Architecture

```
Client ── GraphQL (FastAPI + Strawberry) ── RagService
                                              ├─ chunking       (paragraph-aware splitter)
                                              ├─ Embedder       (hash | OpenAI)
                                              ├─ VectorStore    (SQLite + numpy cosine search)
                                              ├─ Database       (SQLite: documents, chunks, vectors)
                                              └─ LLM            (extractive | OpenAI | Anthropic)
```

Every pipeline stage is an abstract interface (`Embedder`, `VectorStore`, `LLM`),
so new backends are drop-in additions — see [Contributing](#contributing).

## Development

```bash
pip install -e ".[dev]"
ruff check .          # lint
pytest -v             # tests run fully offline
```

## Roadmap / good first issues

- [ ] Additional vector store backends: Qdrant, Weaviate, Redis/Valkey, pgvector, FAISS
- [ ] Additional embedding backends: sentence-transformers (local), Cohere, Voyage
- [ ] Streaming answers via GraphQL subscriptions
- [ ] Metadata filters on `search` (tags, date ranges) and hybrid keyword+vector search
- [ ] Auth (API keys / JWT) and rate limiting
- [ ] Query/embedding caching
- [ ] Auto-generated TypeScript client (GraphQL Code Generator)
- [ ] Evaluation harness with known Q&A pairs; Prometheus metrics
- [ ] Advanced RAG: query rewriting, multi-hop retrieval, citation spans

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for setup,
style, and PR guidelines, and the issue tracker for `good first issue` labels.

## License

[MIT](LICENSE)
