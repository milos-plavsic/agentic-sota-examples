from __future__ import annotations

import shared.data_sources as ds
import shared.data_sources.wikipedia as wiki


def test_wikipedia_fallback_when_remote_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(wiki, "fetch_json_with_cache", lambda *args, **kwargs: None)
    out = ds.fetch_wikipedia_summary("Any topic")
    assert out.used_fallback is True
    assert out.source.startswith("fixture://")
    assert "Fallback" in out.content
