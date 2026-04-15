from __future__ import annotations

from urllib.parse import quote

from shared.data_sources.base import SourceRecord, fetch_json_with_cache


def fetch_github_repo_summary(repo_full_name: str) -> SourceRecord:
    slug = quote(repo_full_name.strip(), safe="/")
    url = f"https://api.github.com/repos/{slug}"
    payload = fetch_json_with_cache(url)
    if payload:
        desc = str(payload.get("description") or "No description")
        stars = payload.get("stargazers_count", 0)
        content = f"{repo_full_name}: {desc}. Stars={stars}."
        return SourceRecord(
            source=url,
            content=content,
            used_fallback=False,
            status_code=200,
            latency_ms=0,
        )
    fallback = (
        f"Fallback GitHub repo summary for {repo_full_name}: public GitHub API unavailable."
    )
    return SourceRecord(
        source="fixture://github-public",
        content=fallback,
        used_fallback=True,
        status_code=503,
        latency_ms=0,
    )
