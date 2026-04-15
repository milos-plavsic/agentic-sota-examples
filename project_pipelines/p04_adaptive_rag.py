from __future__ import annotations

from shared.data_sources import fetch_wikipedia_summary
from shared.runtime import RunState, run_graph


def _proposer(state: RunState) -> str:
    k = min(3 + int(state["iteration"]), 8)
    return (
        f"Adaptive RAG strategy: retrieve top-{k} chunks, expand query, rerank citations, "
        "and re-check hallucination risk before finalization."
    )


def run(cfg: dict[str, object]) -> dict[str, object]:
    return run_graph(
        cfg=cfg,
        source_fetcher=lambda topic: fetch_wikipedia_summary(topic).__dict__,
        proposer=_proposer,
        estimated_cost_usd=0.003,
    )
