from __future__ import annotations

from urllib.parse import quote

from shared.data_sources.base import SourceRecord, fetch_json_with_cache


def fetch_hf_dataset_card(dataset_id: str) -> SourceRecord:
    url = f"https://huggingface.co/api/datasets/{quote(dataset_id)}"
    payload = fetch_json_with_cache(url)
    if payload:
        card = str(payload.get("cardData") or payload.get("description") or "No dataset card")
        content = f"{dataset_id}: {card[:500]}"
        return SourceRecord(
            source=url,
            content=content,
            used_fallback=False,
            status_code=200,
            latency_ms=0,
        )
    fallback = f"Fallback dataset card for {dataset_id}: HuggingFace public API unavailable."
    return SourceRecord(
        source="fixture://hf-public",
        content=fallback,
        used_fallback=True,
        status_code=503,
        latency_ms=0,
    )
