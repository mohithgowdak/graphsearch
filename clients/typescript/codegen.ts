import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  schema: "schema.graphql",
  documents: "src/operations.graphql",
  generates: {
    "src/generated/sdk.ts": {
      plugins: [
        "typescript",
        "typescript-operations",
        "typescript-graphql-request",
      ],
      config: {
        rawRequest: false,
        documentMode: "graphQLTag",
      },
    },
  },
};

export default config;
