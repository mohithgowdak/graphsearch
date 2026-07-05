from graphsearch.llm import ExtractiveLLM, build_prompt
from graphsearch.vectorstore import SearchHit


def hit(text: str, title: str | None = None) -> SearchHit:
    return SearchHit(
        chunk_id="c1", document_id="d1", document_title=title, text=text, score=0.9
    )


def test_build_prompt_numbers_passages_with_titles():
    prompt = build_prompt(
        "What is the policy?",
        [hit("Returns within 30 days.", title="returns"), hit("Ship in 3 days.")],
    )
    assert "[1] (returns)\nReturns within 30 days." in prompt
    assert "[2]\nShip in 3 days." in prompt
    assert prompt.index("[1]") < prompt.index("[2]")
    assert "Cite the passages" in prompt


def test_build_prompt_handles_no_context():
    prompt = build_prompt("Anything?", [])
    assert "(no context found)" in prompt


def test_extractive_llm_returns_top_passages():
    answer = ExtractiveLLM().generate("q", [hit("The support email is help@example.com.")])
    assert "help@example.com" in answer


def test_extractive_llm_handles_no_sources():
    answer = ExtractiveLLM().generate("q", [])
    assert "No relevant documents" in answer
