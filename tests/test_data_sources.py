from __future__ import annotations

from shared.data_sources import (
    fetch_arxiv_snippet,
    fetch_github_repo_summary,
    fetch_hf_dataset_card,
    fetch_uci_dataset_note,
    fetch_wikipedia_summary,
)


def test_public_data_sources_return_content() -> None:
    records = [
        fetch_wikipedia_summary("Machine learning"),
        fetch_arxiv_snippet("large language models"),
        fetch_github_repo_summary("langchain-ai/langgraph"),
        fetch_hf_dataset_card("stanfordnlp/imdb"),
        fetch_uci_dataset_note("student performance"),
    ]
    for record in records:
        assert record.source
        assert isinstance(record.content, str)
        assert len(record.content) > 10
        assert isinstance(record.used_fallback, bool)
