from __future__ import annotations

from shared.data_sources import fetch_arxiv_snippet
from shared.runtime import RunState, run_graph


def _proposer(state: RunState) -> str:
    analyst = "Analyst: identify strongest evidence from sources."
    skeptic = "Skeptic: highlight uncertainty and missing support."
    judge = "Judge: synthesize final recommendation with confidence rationale."
    return (
        f"{analyst} {skeptic} {judge} Debate cycle iteration={state['iteration']} "
        "with consistency checks between personas."
    )


def run(cfg: dict[str, object]) -> dict[str, object]:
    return run_graph(
        cfg=cfg,
        source_fetcher=lambda topic: fetch_arxiv_snippet(topic).__dict__,
        proposer=_proposer,
        estimated_cost_usd=0.004,
    )
