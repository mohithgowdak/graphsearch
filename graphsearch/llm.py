"""LLM backends for answer generation.

Three implementations ship out of the box:

- ``ExtractiveLLM`` — no API key needed. Returns the most relevant retrieved
  passages verbatim. Useful for demos, tests, and CI.
- ``OpenAILLM`` — chat completion via the OpenAI API.
- ``AnthropicLLM`` — messages via the Anthropic API (Claude).

To add another provider, subclass ``LLM`` and register it in ``create_llm``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .config import Settings

PROMPT_TEMPLATE = """\
Answer the question using ONLY the context passages below. If the context does
not contain the answer, say you don't know rather than guessing.

Context:
{context}

Question: {question}

Answer:"""


def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(no context found)"
    return PROMPT_TEMPLATE.format(context=context, question=question)


class LLM(ABC):
    @abstractmethod
    def generate(self, question: str, context_chunks: list[str]) -> str:
        """Produce an answer to ``question`` grounded in ``context_chunks``."""


class ExtractiveLLM(LLM):
    """Key-free fallback: returns the top retrieved passages as the answer."""

    def generate(self, question: str, context_chunks: list[str]) -> str:
        if not context_chunks:
            return "No relevant documents found for this question."
        passages = "\n\n".join(context_chunks[:2])
        return (
            "[extractive mode — configure GRAPHSEARCH_LLM=openai or anthropic "
            "for generated answers]\n\nMost relevant passages:\n\n" + passages
        )


class OpenAILLM(LLM):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "The 'openai' package is required for GRAPHSEARCH_LLM=openai. "
                "Install it with: pip install graphsearch[openai]"
            ) from exc
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY must be set for GRAPHSEARCH_LLM=openai")
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def generate(self, question: str, context_chunks: list[str]) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": build_prompt(question, context_chunks)}],
        )
        return response.choices[0].message.content or ""


class AnthropicLLM(LLM):
    def __init__(self, api_key: str, model: str = "claude-sonnet-5") -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "The 'anthropic' package is required for GRAPHSEARCH_LLM=anthropic. "
                "Install it with: pip install graphsearch[anthropic]"
            ) from exc
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY must be set for GRAPHSEARCH_LLM=anthropic")
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def generate(self, question: str, context_chunks: list[str]) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "user", "content": build_prompt(question, context_chunks)}],
        )
        return "".join(block.text for block in response.content if block.type == "text")


def create_llm(settings: Settings) -> LLM:
    if settings.llm == "extractive":
        return ExtractiveLLM()
    if settings.llm == "openai":
        return OpenAILLM(settings.openai_api_key, settings.openai_model)
    if settings.llm == "anthropic":
        return AnthropicLLM(settings.anthropic_api_key, settings.anthropic_model)
    raise ValueError(f"Unknown LLM backend: {settings.llm!r}")
