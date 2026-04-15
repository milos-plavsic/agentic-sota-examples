from __future__ import annotations

import time
from urllib.parse import quote

from shared.data_sources.base import SourceRecord, fetch_json_with_cache


def fetch_wikipedia_summary(topic: str) -> SourceRecord:
    safe_topic = quote(topic.strip().replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_topic}"
    t0 = time.perf_counter()
    payload = fetch_json_with_cache(url)
    latency_ms = int((time.perf_counter() - t0) * 1000)
    if payload:
        text = str(payload.get("extract") or "").strip()
        if text:
            return SourceRecord(
                source=url,
                content=text,
                used_fallback=False,
                status_code=200,
                latency_ms=latency_ms,
            )
    fallback = (
        f"Fallback summary for {topic}: live Wikipedia summary unavailable; "
        "using deterministic fixture content."
    )
    return SourceRecord(
        source="fixture://wikipedia-summary",
        content=fallback,
        used_fallback=True,
        status_code=503,
        latency_ms=latency_ms,
    )
