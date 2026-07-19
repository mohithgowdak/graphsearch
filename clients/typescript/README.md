# @graphsearch/client

A fully-typed TypeScript client for the [GraphSearch](../../README.md) GraphQL
API, generated from the live schema with
[GraphQL Code Generator](https://the-guild.dev/graphql/codegen). No hand-written
request/response types — they're regenerated from `graphsearch/schema.py`
itself, so they can't drift out of sync with the server without CI catching it.

## Install

This package isn't published yet — for now, use it from within the monorepo
or copy `src/` into your project.

```bash
cd clients/typescript
npm install
```

## Usage

```ts
import { createGraphSearchClient } from "@graphsearch/client";

const client = createGraphSearchClient("http://localhost:8000/graphql");

const { answer } = await client.Answer({ question: "How do I get my money back?" });

console.log(answer.text);
answer.sources.forEach((source, i) => {
  console.log(`[${i + 1}] ${source.documentTitle}: ${source.text} (score: ${source.score})`);
});
```

Every field above is type-checked against the real schema — rename a field on
the server (e.g. `documentTitle`) and this code stops compiling until it's
updated, instead of failing silently at runtime.

Available functions: `Answer`, `Search`, `Documents`, `Document`,
`UploadDocument`, `DeleteDocument` — one per operation defined in
[`src/operations.graphql`](src/operations.graphql).

> **Note:** `uploadFile` (PDF/Markdown/text file uploads) is intentionally
> **not** included in this generated SDK. It's a GraphQL multipart request
> (file bytes over `FormData`), which needs upload-aware request handling that
> `graphql-request`'s default SDK doesn't provide out of the box. The
> `uploadFile` mutation is still fully typed in `schema.graphql` and the base
> generated types — adding a typed multipart helper for it is a good follow-up
> issue.

## Regenerating the client

If the GraphQL schema changes (a field is added, renamed, etc.), regenerate
everything with:

```bash
# from the repo root, with the Python package installed:
strawberry export-schema graphsearch.schema:schema -o clients/typescript/schema.graphql

# from clients/typescript/:
npm run codegen
```

CI runs these same two commands on every push/PR and fails the build if the
regenerated output doesn't match what's committed — so it's not possible to
merge a schema change without also updating this client.
