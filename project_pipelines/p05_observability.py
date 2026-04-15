from __future__ import annotations

from shared.data_sources import fetch_github_repo_summary
from shared.runtime import RunState, run_graph


def _proposer(state: RunState) -> str:
    return (
        "Observability-first execution: emit node-level traces, confidence trajectory, "
        f"and latency-aware diagnostics for iteration={state['iteration']}."
    )


def run(cfg: dict[str, object]) -> dict[str, object]:
    cfg = {**cfg, "topic": "open-telemetry/opentelemetry-python"}
    return run_graph(
        cfg=cfg,
        source_fetcher=lambda repo: fetch_github_repo_summary(repo).__dict__,
        proposer=_proposer,
        estimated_cost_usd=0.001,
    )
