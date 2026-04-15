from __future__ import annotations

from shared.data_sources import fetch_wikipedia_summary
from shared.runtime import RunState, run_graph


def _proposer(state: RunState) -> str:
    model_tier = "cheap-model" if int(state["iteration"]) == 1 else "strong-model"
    return (
        f"Cost-quality router selects {model_tier}, compares risk budget, and escalates only "
        f"when confidence is below threshold (iteration={state['iteration']})."
    )


def run(cfg: dict[str, object]) -> dict[str, object]:
    result = run_graph(
        cfg=cfg,
        source_fetcher=lambda topic: fetch_wikipedia_summary(topic).__dict__,
        proposer=_proposer,
        estimated_cost_usd=0.0005,
    )
    score = float(result["confidence_score"])
    result["router_benchmark"] = {
        "router_score": score,
        "always_cheap_score": max(score - 0.05, 0.0),
        "always_strong_score": min(score + 0.03, 1.0),
    }
    return result
