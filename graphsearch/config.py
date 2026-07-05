"""Application configuration, loaded from environment variables / .env file.

All GraphSearch-specific settings use the ``GRAPHSEARCH_`` prefix
(e.g. ``GRAPHSEARCH_LLM=openai``). Provider API keys use their
conventional names: ``OPENAI_API_KEY`` and ``ANTHROPIC_API_KEY``.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GRAPHSEARCH_", env_file=".env", extra="ignore"
    )

    # Storage
    database_path: str = "graphsearch.db"

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 100

    # Retrieval
    default_top_k: int = 4

    # Backends: which implementation to use for each pipeline stage.
    #   embeddings: "hash" (offline, no key needed) or "openai"
    #   llm: "extractive" (offline), "openai", or "anthropic"
    embeddings: str = "hash"
    llm: str = "extractive"

    # Model names (only used when the matching backend is selected)
    openai_embedding_model: str = "text-embedding-3-small"
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-sonnet-5"

    # Provider keys (no prefix — conventional env var names)
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
