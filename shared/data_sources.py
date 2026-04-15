"""Compatibility re-export for canonical data source package."""

from shared.data_sources import (
    SourceRecord,
    fetch_arxiv_snippet,
    fetch_github_repo_summary,
    fetch_hf_dataset_card,
    fetch_uci_dataset_note,
    fetch_wikipedia_summary,
)

__all__ = [
    "SourceRecord",
    "fetch_wikipedia_summary",
    "fetch_arxiv_snippet",
    "fetch_github_repo_summary",
    "fetch_hf_dataset_card",
    "fetch_uci_dataset_note",
]
