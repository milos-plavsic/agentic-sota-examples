from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, StateGraph

from shared.evals import score_text_answer
from shared.orchestration_policy import confidence_label, decide_loop
from shared.telemetry import emit_trace


class RunState(TypedDict, total=False):
    project: str
    task: str
    topic: str
    confidence_threshold: float
    max_iterations: int
    iteration: int
    source: str
    source_context: str
    used_fallback: bool
    source_latency_ms: int
    answer: str
    confidence_score: float
    confidence_label: str
    continue_loop: bool
    loop_terminated_reason: str
    iteration_history: list[dict[str, float | int]]
    decision_log: list[str]
    trace_events: list[dict[str, object]]


SourceFetcher = Callable[[str], dict[str, object]]
Proposer = Callable[[RunState], str]


def run_graph(
    *,
    cfg: dict[str, object],
    source_fetcher: SourceFetcher,
    proposer: Proposer,
    estimated_cost_usd: float = 0.0,
) -> dict[str, object]:
    root = Path(__file__).resolve().parents[1]
    project_name = str(cfg["project"])

    def _fetch_source(state: RunState) -> RunState:
        rec = source_fetcher(str(state["topic"]))
        trace = list(state.get("trace_events", []))
        trace.append({"node": "fetch", "source": rec["source"], "fallback": rec["used_fallback"]})
        return {
            "source": str(rec["source"]),
            "source_context": str(rec["content"]),
            "used_fallback": bool(rec["used_fallback"]),
            "source_latency_ms": int(rec.get("latency_ms", 0)),
            "trace_events": trace,
        }

    def _propose(state: RunState) -> RunState:
        answer = proposer(state)
        trace = list(state.get("trace_events", []))
        trace.append({"node": "propose", "answer_len": len(answer), "iteration": state["iteration"]})
        return {"answer": answer, "trace_events": trace}

    def _evaluate(state: RunState) -> RunState:
        iteration = int(state.get("iteration", 1))
        ev = score_text_answer(
            str(state["answer"]),
            str(state["source_context"]),
            iteration,
            latency_ms=int(state.get("source_latency_ms", 0)),
            estimated_cost_usd=estimated_cost_usd,
        )
        label = confidence_label(ev["confidence_score"])
        history = list(state.get("iteration_history", []))
        history.append({"iteration": iteration, **ev})
        trace = list(state.get("trace_events", []))
        trace.append({"node": "evaluate", "confidence_score": ev["confidence_score"]})
        return {
            "confidence_score": ev["confidence_score"],
            "confidence_label": label,
            "iteration_history": history,
            "trace_events": trace,
        }

    def _assess_and_decide(state: RunState) -> RunState:
        iteration = int(state.get("iteration", 1))
        decision = decide_loop(
            confidence_score=float(state["confidence_score"]),
            confidence_threshold=float(state["confidence_threshold"]),
            iteration=iteration,
            max_iterations=int(state["max_iterations"]),
        )
        logs = list(state.get("decision_log", []))
        logs.append(decision["stop_reason"])
        trace = list(state.get("trace_events", []))
        trace.append({"node": "assess", "decision": decision["stop_reason"]})
        return {
            "continue_loop": decision["continue_loop"],
            "loop_terminated_reason": decision["stop_reason"],
            "decision_log": logs,
            "trace_events": trace,
        }

    def _route(state: RunState) -> str:
        return "retry" if bool(state.get("continue_loop")) else "finalize"

    def _retry(state: RunState) -> RunState:
        return {"iteration": int(state.get("iteration", 1)) + 1}

    graph = StateGraph(RunState)
    graph.add_node("fetch", _fetch_source)
    graph.add_node("propose", _propose)
    graph.add_node("evaluate", _evaluate)
    graph.add_node("assess", _assess_and_decide)
    graph.add_node("retry", _retry)
    graph.add_node("finalize", lambda s: s)
    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "propose")
    graph.add_edge("propose", "evaluate")
    graph.add_edge("evaluate", "assess")
    graph.add_conditional_edges("assess", _route, {"retry": "retry", "finalize": "finalize"})
    graph.add_edge("retry", "propose")
    graph.add_edge("finalize", END)
    app = graph.compile()

    initial: RunState = {
        "project": project_name,
        "task": str(cfg["task"]),
        "topic": str(cfg["topic"]),
        "confidence_threshold": float(cfg.get("confidence_threshold", 0.7)),
        "max_iterations": int(cfg.get("max_iterations", 3)),
        "iteration": 1,
        "iteration_history": [],
        "decision_log": [],
        "trace_events": [],
    }
    out: RunState = app.invoke(initial)

    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    summary_path = reports_dir / f"{project_name}-summary.json"
    report_path = reports_dir / f"{project_name}-REPORT.md"

    result: dict[str, object] = {
        "project": out["project"],
        "task": out["task"],
        "confidence_threshold": out["confidence_threshold"],
        "iterations": out["iteration"],
        "confidence_score": out["confidence_score"],
        "confidence_label": out["confidence_label"],
        "loop_terminated_reason": out["loop_terminated_reason"],
        "iteration_history": out["iteration_history"],
        "decision_log": out["decision_log"],
        "source": out["source"],
        "used_fallback": out["used_fallback"],
        "answer": out["answer"],
    }
    trace_path = emit_trace(project_name, list(out.get("trace_events", [])))
    result["summary_path"] = str(summary_path)
    result["report_path"] = str(report_path)
    result["trace_path"] = trace_path

    summary_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    report_path.write_text(
        (
            f"# {project_name} Report\n\n"
            f"- Task: {result['task']}\n"
            f"- Confidence: {result['confidence_score']:.3f} ({result['confidence_label']})\n"
            f"- Iterations: {result['iterations']}\n"
            f"- Stop reason: {result['loop_terminated_reason']}\n"
            f"- Source: {result['source']}\n"
            f"- Used fallback: {result['used_fallback']}\n"
        ),
        encoding="utf-8",
    )
    return result
