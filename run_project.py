from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from project_pipelines import PROJECT_RUNNERS

ROOT = Path(__file__).resolve().parent
VALID_LOOP_REASONS = {
    "confidence_threshold_reached",
    "max_iterations_reached",
    "retry_with_additional_information",
}


def _load_config(project_name: str) -> dict[str, object]:
    """Load config.."""
    cfg_path = ROOT / "projects" / project_name / "project.json"
    data: dict[str, object] = json.loads(cfg_path.read_text(encoding="utf-8"))
    return data


def run_project_with_config(
    project_name: str, cfg_overrides: dict[str, object] | None = None
) -> dict[str, object]:
    """Run project with config."""
    cfg = _load_config(project_name)
    if cfg_overrides:
        cfg.update(cfg_overrides)
    runner = PROJECT_RUNNERS.get(project_name)
    if runner is None:
        raise ValueError(f"Unsupported project name: {project_name}")
    return _normalise_result(project_name, cfg, runner(cfg))


def _confidence_label(score: float) -> str:
    """Convert a numeric confidence score into the public label enum."""
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _normalise_stop_reason(reason: str, score: float, threshold: float) -> str:
    """Map project-specific stop reasons onto the public contract enum."""
    if reason in VALID_LOOP_REASONS:
        return reason
    if reason in {"consensus_reached", "accepted", "passed_guardrails", "routed"}:
        return "confidence_threshold_reached"
    if score >= threshold:
        return "confidence_threshold_reached"
    return "max_iterations_reached"


def _coerce_history(raw: Any, iterations: int, score: float) -> list[dict[str, object]]:
    """Return an iteration history with one entry per reported iteration."""
    if isinstance(raw, list) and raw:
        history = [dict(item) if isinstance(item, dict) else {"value": item} for item in raw]
    else:
        history = [{"iteration": i + 1, "confidence_score": score} for i in range(iterations)]
    while len(history) < iterations:
        history.append({"iteration": len(history) + 1, "confidence_score": score})
    return history[:iterations]


def _write_artifacts(project_name: str, result: dict[str, object]) -> None:
    """Persist the summary, report, and trace artifacts required by the contract."""
    reports_dir = ROOT / "reports"
    traces_dir = ROOT / "traces"
    reports_dir.mkdir(parents=True, exist_ok=True)
    traces_dir.mkdir(parents=True, exist_ok=True)

    summary_path = reports_dir / f"{project_name}-summary.json"
    report_path = reports_dir / f"{project_name}-REPORT.md"
    trace_path = traces_dir / f"{project_name}-trace.json"

    result["summary_path"] = str(summary_path)
    result["report_path"] = str(report_path)
    result["trace_path"] = str(trace_path)

    summary_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    trace_path.write_text(
        json.dumps(
            {
                "project": project_name,
                "iterations": result["iterations"],
                "decision_log": result["decision_log"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    report_path.write_text(
        (
            f"# {project_name} Report\n\n"
            f"- Task: {result['task']}\n"
            f"- Confidence: {float(result['confidence_score']):.3f} "
            f"({result['confidence_label']})\n"
            f"- Iterations: {result['iterations']}\n"
            f"- Stop reason: {result['loop_terminated_reason']}\n"
            f"- Source: {result['source']}\n"
            f"- Used fallback: {result['used_fallback']}\n"
        ),
        encoding="utf-8",
    )


def _normalise_result(
    project_name: str, cfg: dict[str, object], raw: dict[str, object]
) -> dict[str, object]:
    """Adapt each pipeline's native output to the stable project contract."""
    threshold = float(cfg.get("confidence_threshold", 0.7))
    score = float(raw.get("confidence_score", raw.get("score", 0.0)))
    score = max(0.0, min(score, 1.0))
    iterations = int(raw.get("iterations", raw.get("rounds_completed", 1)))
    iterations = max(iterations, 1)
    stop_reason = _normalise_stop_reason(
        str(raw.get("loop_terminated_reason", raw.get("stop_reason", ""))),
        score,
        threshold,
    )
    history = _coerce_history(
        raw.get("iteration_history", raw.get("score_history", raw.get("rounds", []))),
        iterations,
        score,
    )
    decision_log = list(raw.get("decision_log", []))
    if len(decision_log) != iterations:
        decision_log = [stop_reason for _ in range(iterations)]

    result = dict(raw)
    result.update(
        {
            "project": project_name,
            "task": str(cfg.get("task", raw.get("task", ""))),
            "topic": str(cfg.get("topic", raw.get("topic", ""))),
            "confidence_threshold": threshold,
            "iterations": iterations,
            "confidence_score": score,
            "confidence_label": str(raw.get("confidence_label", _confidence_label(score))),
            "loop_terminated_reason": stop_reason,
            "iteration_history": history,
            "decision_log": decision_log,
            "source": str(raw.get("source", raw.get("source_name", "local_fallback"))),
            "used_fallback": bool(raw.get("used_fallback", False)),
            "answer": str(raw.get("answer", raw.get("verdict", raw.get("recommendation", "")))),
        }
    )
    _write_artifacts(project_name, result)
    return result


def run_project(project_name: str) -> dict[str, object]:
    """Run project."""
    return run_project_with_config(project_name)


def main() -> None:
    """Main."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Project folder name")
    parser.add_argument(
        "--overrides-json",
        default="",
        help="Optional JSON object to override project config (task/topic/threshold/etc).",
    )
    args = parser.parse_args()

    overrides: dict[str, object] | None = None
    if args.overrides_json:
        overrides = json.loads(args.overrides_json)
    result = run_project_with_config(args.project, overrides)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
