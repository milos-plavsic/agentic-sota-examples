# ruff: noqa: I001
from __future__ import annotations

from pathlib import Path

from shared.telemetry import emit_trace

from agent_core.langgraph_runtime import EvalLoopState, run_eval_loop_graph

RunState = EvalLoopState


def run_graph(
    *,
    cfg: dict[str, object],
    source_fetcher,
    proposer,
    estimated_cost_usd: float = 0.0,
) -> dict[str, object]:
    """Run the shared confidence-gated LangGraph loop via agent-core."""
    root = Path(__file__).resolve().parents[1]
    reports_dir = root / "reports"
    result = run_eval_loop_graph(
        cfg=cfg,
        source_fetcher=source_fetcher,
        proposer=proposer,
        reports_dir=reports_dir,
        estimated_cost_usd=estimated_cost_usd,
    )
    project_name = str(cfg["project"])
    trace_path = emit_trace(project_name, list(result.get("trace_events", [])))
    result["trace_path"] = trace_path
    return dict(result)
