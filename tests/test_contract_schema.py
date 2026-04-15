from __future__ import annotations

from run_project import run_project

REQUIRED_FIELDS = {
    "project",
    "task",
    "confidence_threshold",
    "iterations",
    "confidence_score",
    "confidence_label",
    "loop_terminated_reason",
    "iteration_history",
    "decision_log",
    "source",
    "used_fallback",
    "answer",
    "summary_path",
    "report_path",
    "trace_path",
}


def test_contract_schema_types_and_enums() -> None:
    out = run_project("01-eval-driven-agent")
    assert REQUIRED_FIELDS.issubset(out.keys())
    assert isinstance(out["project"], str)
    assert isinstance(out["task"], str)
    assert isinstance(out["confidence_threshold"], float)
    assert isinstance(out["iterations"], int)
    assert isinstance(out["confidence_score"], float)
    assert out["confidence_label"] in {"low", "medium", "high"}
    assert out["loop_terminated_reason"] in {
        "confidence_threshold_reached",
        "max_iterations_reached",
        "retry_with_additional_information",
    }
    assert isinstance(out["iteration_history"], list)
    assert isinstance(out["decision_log"], list)
