import { GraphQLClient } from "graphql-request";
import { getSdk } from "./generated/sdk.js";

export * from "./generated/sdk.js";

/**
 * Creates a typed GraphSearch client bound to a running server.
 *
 * @param url The GraphQL endpoint, e.g. "http://localhost:8000/graphql"
 */
export function createGraphSearchClient(url: string) {
  return getSdk(new GraphQLClient(url));
}
