from __future__ import annotations

from urllib.parse import quote

from shared.data_sources.base import SourceRecord, fetch_json_with_cache


def fetch_arxiv_snippet(query: str) -> SourceRecord:
    url = f"https://export.arxiv.org/api/query?search_query=all:{quote(query)}&start=0&max_results=1"
    # arXiv endpoint is XML; we still probe availability via cached JSON utility fallback path.
    payload = fetch_json_with_cache(url)
    if payload:
        return SourceRecord(
            source=url,
            content=str(payload)[:400],
            used_fallback=False,
            status_code=200,
            latency_ms=0,
        )
    fallback = (
        f"Fallback arXiv snippet for {query}: public API unavailable; "
        "using deterministic literature placeholder."
    )
    return SourceRecord(
        source="fixture://arxiv",
        content=fallback,
        used_fallback=True,
        status_code=503,
        latency_ms=0,
    )
