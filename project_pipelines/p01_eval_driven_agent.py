from __future__ import annotations

from shared.data_sources import fetch_wikipedia_summary
from shared.runtime import RunState, run_graph


def _proposer(state: RunState) -> str:
    return (
        "Eval-driven refinement strategy: propose an answer, score quality/calibration/cost, "
        f"then iterate. Current iteration={state['iteration']}."
    )


def run(cfg: dict[str, object]) -> dict[str, object]:
    return run_graph(
        cfg=cfg,
        source_fetcher=lambda topic: fetch_wikipedia_summary(topic).__dict__,
        proposer=_proposer,
        estimated_cost_usd=0.002,
    )
