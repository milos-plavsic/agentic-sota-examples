from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


@dataclass(frozen=True)
class SourceRecord:
    source: str
    content: str
    used_fallback: bool
    status_code: int
    latency_ms: int


def _cache_dir() -> Path:
    root = Path(__file__).resolve().parents[2]
    cache = root / ".cache" / "sources"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def fetch_json_with_cache(url: str, *, timeout_s: float = 8.0, retries: int = 2) -> dict[str, Any] | None:
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()
    cache_file = _cache_dir() / f"{key}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    headers = {"User-Agent": "agentic-sota-examples/1.0"}
    for _ in range(max(retries, 1)):
        try:
            with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                payload: dict[str, Any] = response.json()
                cache_file.write_text(json.dumps(payload), encoding="utf-8")
                return payload
        except Exception:
            time.sleep(0.15)
            continue
    return None
