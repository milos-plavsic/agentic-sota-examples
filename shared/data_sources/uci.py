from __future__ import annotations

from urllib.parse import quote

from shared.data_sources.base import SourceRecord, fetch_json_with_cache


def fetch_uci_dataset_note(dataset_name: str) -> SourceRecord:
    # Public endpoint with metadata entries for UCI dataset records.
    url = f"https://archive.ics.uci.edu/api/dataset/list?search={quote(dataset_name)}"
    payload = fetch_json_with_cache(url)
    if payload:
        items = payload.get("data", [])
        first = items[0] if items else {}
        name = first.get("name", dataset_name)
        content = f"UCI dataset {name}. Metadata records available: {len(items)}."
        return SourceRecord(
            source=url,
            content=content,
            used_fallback=False,
            status_code=200,
            latency_ms=0,
        )
    fallback = f"Fallback UCI metadata note for {dataset_name}: UCI API unavailable."
    return SourceRecord(
        source="fixture://uci",
        content=fallback,
        used_fallback=True,
        status_code=503,
        latency_ms=0,
    )
