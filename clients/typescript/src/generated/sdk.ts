import { GraphQLClient, RequestOptions } from 'graphql-request';
import gql from 'graphql-tag';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
type GraphQLClientRequestHeaders = RequestOptions['requestHeaders'];
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  /** Represents a file upload. */
  Upload: { input: any; output: any; }
};

export type Answer = {
  __typename?: 'Answer';
  /** Retrieved passages; citations like [1] in `text` are 1-indexed into this list. */
  sources: Array<Chunk>;
  text: Scalars['String']['output'];
};

export type Chunk = {
  __typename?: 'Chunk';
  documentId: Scalars['ID']['output'];
  documentTitle?: Maybe<Scalars['String']['output']>;
  id: Scalars['ID']['output'];
  score: Scalars['Float']['output'];
  text: Scalars['String']['output'];
};

export type Document = {
  __typename?: 'Document';
  chunkCount: Scalars['Int']['output'];
  content: Scalars['String']['output'];
  createdAt: Scalars['String']['output'];
  id: Scalars['ID']['output'];
  source?: Maybe<Scalars['String']['output']>;
  title?: Maybe<Scalars['String']['output']>;
};

export type Mutation = {
  __typename?: 'Mutation';
  /** Delete a document and its indexed chunks. */
  deleteDocument: Scalars['Boolean']['output'];
  /** Ingest a document: it is chunked, embedded, and indexed. */
  uploadDocument: Document;
  /** Upload a file (PDF, Markdown, or plain text): its text is extracted, chunked, embedded, and indexed. Sent as a GraphQL multipart request. */
  uploadFile: Document;
};


export type MutationDeleteDocumentArgs = {
  id: Scalars['ID']['input'];
};


export type MutationUploadDocumentArgs = {
  content: Scalars['String']['input'];
  source?: InputMaybe<Scalars['String']['input']>;
  title?: InputMaybe<Scalars['String']['input']>;
};


export type MutationUploadFileArgs = {
  file: Scalars['Upload']['input'];
  source?: InputMaybe<Scalars['String']['input']>;
  title?: InputMaybe<Scalars['String']['input']>;
};

export type Query = {
  __typename?: 'Query';
  /** Ask a question and get an answer grounded in your documents. */
  answer: Answer;
  /** Fetch a single document by ID. */
  document?: Maybe<Document>;
  /** List ingested documents, newest first. */
  documents: Array<Document>;
  /** Semantic search: return the most relevant chunks for a query. */
  search: Array<Chunk>;
};


export type QueryAnswerArgs = {
  question: Scalars['String']['input'];
  topK?: InputMaybe<Scalars['Int']['input']>;
};


export type QueryDocumentArgs = {
  id: Scalars['ID']['input'];
};


export type QueryDocumentsArgs = {
  limit?: Scalars['Int']['input'];
  offset?: Scalars['Int']['input'];
};


export type QuerySearchArgs = {
  query: Scalars['String']['input'];
  topK?: InputMaybe<Scalars['Int']['input']>;
};

export type AnswerQueryVariables = Exact<{
  question: Scalars['String']['input'];
  topK?: InputMaybe<Scalars['Int']['input']>;
}>;


export type AnswerQuery = { __typename?: 'Query', answer: { __typename?: 'Answer', text: string, sources: Array<{ __typename?: 'Chunk', id: string, documentId: string, documentTitle?: string | null, text: string, score: number }> } };

export type SearchQueryVariables = Exact<{
  query: Scalars['String']['input'];
  topK?: InputMaybe<Scalars['Int']['input']>;
}>;


export type SearchQuery = { __typename?: 'Query', search: Array<{ __typename?: 'Chunk', id: string, documentId: string, documentTitle?: string | null, text: string, score: number }> };

export type DocumentsQueryVariables = Exact<{
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
}>;


export type DocumentsQuery = { __typename?: 'Query', documents: Array<{ __typename?: 'Document', id: string, title?: string | null, source?: string | null, createdAt: string, chunkCount: number }> };

export type DocumentQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type DocumentQuery = { __typename?: 'Query', document?: { __typename?: 'Document', id: string, title?: string | null, source?: string | null, content: string, createdAt: string, chunkCount: number } | null };

export type UploadDocumentMutationVariables = Exact<{
  content: Scalars['String']['input'];
  title?: InputMaybe<Scalars['String']['input']>;
  source?: InputMaybe<Scalars['String']['input']>;
}>;


export type UploadDocumentMutation = { __typename?: 'Mutation', uploadDocument: { __typename?: 'Document', id: string, title?: string | null, source?: string | null, createdAt: string, chunkCount: number } };

export type DeleteDocumentMutationVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type DeleteDocumentMutation = { __typename?: 'Mutation', deleteDocument: boolean };


export const AnswerDocument = gql`
    query Answer($question: String!, $topK: Int) {
  answer(question: $question, topK: $topK) {
    text
    sources {
      id
      documentId
      documentTitle
      text
      score
    }
  }
}
    `;
export const SearchDocument = gql`
    query Search($query: String!, $topK: Int) {
  search(query: $query, topK: $topK) {
    id
    documentId
    documentTitle
    text
    score
  }
}
    `;
export const DocumentsDocument = gql`
    query Documents($limit: Int, $offset: Int) {
  documents(limit: $limit, offset: $offset) {
    id
    title
    source
    createdAt
    chunkCount
  }
}
    `;
export const DocumentDocument = gql`
    query Document($id: ID!) {
  document(id: $id) {
    id
    title
    source
    content
    createdAt
    chunkCount
  }
}
    `;
export const UploadDocumentDocument = gql`
    mutation UploadDocument($content: String!, $title: String, $source: String) {
  uploadDocument(content: $content, title: $title, source: $source) {
    id
    title
    source
    createdAt
    chunkCount
  }
}
    `;
export const DeleteDocumentDocument = gql`
    mutation DeleteDocument($id: ID!) {
  deleteDocument(id: $id)
}
    `;

export type SdkFunctionWrapper = <T>(action: (requestHeaders?:Record<string, string>) => Promise<T>, operationName: string, operationType?: string, variables?: any) => Promise<T>;


const defaultWrapper: SdkFunctionWrapper = (action, _operationName, _operationType, _variables) => action();

export function getSdk(client: GraphQLClient, withWrapper: SdkFunctionWrapper = defaultWrapper) {
  return {
    Answer(variables: AnswerQueryVariables, requestHeaders?: GraphQLClientRequestHeaders, signal?: RequestInit['signal']): Promise<AnswerQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<AnswerQuery>({ document: AnswerDocument, variables, requestHeaders: { ...requestHeaders, ...wrappedRequestHeaders }, signal }), 'Answer', 'query', variables);
    },
    Search(variables: SearchQueryVariables, requestHeaders?: GraphQLClientRequestHeaders, signal?: RequestInit['signal']): Promise<SearchQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<SearchQuery>({ document: SearchDocument, variables, requestHeaders: { ...requestHeaders, ...wrappedRequestHeaders }, signal }), 'Search', 'query', variables);
    },
    Documents(variables?: DocumentsQueryVariables, requestHeaders?: GraphQLClientRequestHeaders, signal?: RequestInit['signal']): Promise<DocumentsQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<DocumentsQuery>({ document: DocumentsDocument, variables, requestHeaders: { ...requestHeaders, ...wrappedRequestHeaders }, signal }), 'Documents', 'query', variables);
    },
    Document(variables: DocumentQueryVariables, requestHeaders?: GraphQLClientRequestHeaders, signal?: RequestInit['signal']): Promise<DocumentQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<DocumentQuery>({ document: DocumentDocument, variables, requestHeaders: { ...requestHeaders, ...wrappedRequestHeaders }, signal }), 'Document', 'query', variables);
    },
    UploadDocument(variables: UploadDocumentMutationVariables, requestHeaders?: GraphQLClientRequestHeaders, signal?: RequestInit['signal']): Promise<UploadDocumentMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<UploadDocumentMutation>({ document: UploadDocumentDocument, variables, requestHeaders: { ...requestHeaders, ...wrappedRequestHeaders }, signal }), 'UploadDocument', 'mutation', variables);
    },
    DeleteDocument(variables: DeleteDocumentMutationVariables, requestHeaders?: GraphQLClientRequestHeaders, signal?: RequestInit['signal']): Promise<DeleteDocumentMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<DeleteDocumentMutation>({ document: DeleteDocumentDocument, variables, requestHeaders: { ...requestHeaders, ...wrappedRequestHeaders }, signal }), 'DeleteDocument', 'mutation', variables);
    }
  };
}
export type Sdk = ReturnType<typeof getSdk>;