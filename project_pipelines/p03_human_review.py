from __future__ import annotations

import json
from pathlib import Path

from shared.data_sources import fetch_github_repo_summary
from shared.runtime import RunState, run_graph


def _proposer(state: RunState) -> str:
    escalation = (
        "Escalate to human reviewer if confidence remains below threshold after retry,"
        " attaching evidence snapshot and suggested actions."
    )
    return f"{escalation} iteration={state['iteration']} with resume-ready decision payload."


def run(cfg: dict[str, object]) -> dict[str, object]:
    topic = str(cfg.get("topic", "microsoft/semantic-kernel"))
    source = topic if "/" in topic else "microsoft/semantic-kernel"
    cfg = {**cfg, "topic": source}
    result = run_graph(
        cfg=cfg,
        source_fetcher=lambda repo: fetch_github_repo_summary(repo).__dict__,
        proposer=_proposer,
        estimated_cost_usd=0.0015,
    )
    payload = {
        "title": f"[Review Needed] {result['project']}",
        "body": f"Confidence={result['confidence_score']:.3f}; reason={result['loop_terminated_reason']}",
        "labels": ["human-review", "agentic-workflow"],
    }
    root = Path(__file__).resolve().parents[1]
    out = root / "reports" / f"{result['project']}-review-payload.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    result["review_payload_path"] = str(out)
    return result
