"""Base data source with proper caching and error handling."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from ml_core import DiskCache, configure_logging, retry_with_backoff

logger = configure_logging(__name__)


@dataclass(frozen=True)
class SourceRecord:
    """Cached source record."""

    source: str
    content: str
    used_fallback: bool
    status_code: int
    latency_ms: int


def _cache_dir() -> Path:
    """Get cache directory."""
    root = Path(__file__).resolve().parents[2]
    cache = root / ".cache" / "sources"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


# Initialize disk cache with 24-hour TTL
_disk_cache = DiskCache(_cache_dir(), default_ttl=86400)


def fetch_json_with_cache(
    url: str,
    *,
    timeout_s: float = 8.0,
    retries: int = 2,
    ttl_seconds: int = 86400,  # 24 hours
) -> dict[str, Any] | None:
    """Fetch JSON from URL with disk caching and TTL.

    Args:
        url: URL to fetch
        timeout_s: Request timeout in seconds
        retries: Number of retry attempts
        ttl_seconds: Cache TTL (default 24 hours)

    Returns:
        Parsed JSON or None if all retries failed
    """
    # Validate inputs
    timeout_s = max(1.0, min(timeout_s, 60.0))  # 1-60 seconds
    retries = max(1, min(retries, 10))  # 1-10 retries

    # Try to get from cache first
    cached = _disk_cache.get(url, ttl=ttl_seconds)
    if cached is not None:
        logger.info(f"Cache hit for {url}")
        return cached

    logger.info(f"Fetching from {url}")

    headers = {
        "User-Agent": "agentic-sota-examples/1.0",
        "Accept": "application/json",
    }

    def _fetch() -> dict[str, Any]:
        """Fetch without retry logic."""
        try:
            with httpx.Client(
                timeout=timeout_s,
                follow_redirects=True,
                limits=httpx.Limits(max_connections=5, max_keepalive_connections=2),
            ) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                payload: dict[str, Any] = response.json()

                # Cache the result
                _disk_cache.set(url, payload)
                logger.info(f"Successfully fetched and cached {url}")

                return payload
        except httpx.TimeoutException as e:
            logger.error(f"Timeout fetching {url}: {e}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {url}: {e}")
            raise

    # Retry with exponential backoff
    try:
        return retry_with_backoff(
            _fetch,
            max_retries=retries,
            initial_delay=0.1,
            max_delay=10.0,
            backoff_factor=2.0,
            exceptions=(httpx.HTTPError, json.JSONDecodeError, httpx.TimeoutException),
        )
    except Exception as e:
        logger.error(f"Failed to fetch {url} after {retries} retries: {e}")
        return None
