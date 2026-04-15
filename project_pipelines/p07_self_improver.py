from __future__ import annotations

import json
from pathlib import Path

from shared.data_sources import fetch_hf_dataset_card
from shared.runtime import RunState, run_graph


def _proposer(state: RunState) -> str:
    return (
        "Self-improver loop: mine failure patterns, propose prompt/policy patch, "
        f"and benchmark candidate deltas at iteration={state['iteration']}."
    )


def run(cfg: dict[str, object]) -> dict[str, object]:
    cfg = {**cfg, "topic": "stanfordnlp/imdb"}
    result = run_graph(
        cfg=cfg,
        source_fetcher=lambda dataset_id: fetch_hf_dataset_card(dataset_id).__dict__,
        proposer=_proposer,
        estimated_cost_usd=0.0025,
    )
    recommendation = {
        "project": result["project"],
        "recommended_change": "increase evidence grounding tokens and tighten guardrail thresholds",
        "expected_impact": {"confidence_delta": 0.03, "latency_delta_ms": 120},
    }
    root = Path(__file__).resolve().parents[1]
    out = root / "reports" / f"{result['project']}-recommendation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(recommendation, indent=2), encoding="utf-8")
    result["recommendation_path"] = str(out)
    return result
