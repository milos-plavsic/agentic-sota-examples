from __future__ import annotations

from run_project import run_project
from shared.testing import PROJECTS


def test_all_projects_contract_smoke() -> None:
    required = {
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
    for project in PROJECTS:
        out = run_project(project)
        assert required.issubset(out.keys())
        assert 0.0 <= float(out["confidence_score"]) <= 1.0
        assert out["confidence_label"] in {"low", "medium", "high"}
        assert out["loop_terminated_reason"] in {
            "confidence_threshold_reached",
            "max_iterations_reached",
            "retry_with_additional_information",
        }
        assert isinstance(out["iteration_history"], list)
        assert isinstance(out["decision_log"], list)
        assert len(out["iteration_history"]) == int(out["iterations"])
        assert len(out["decision_log"]) == int(out["iterations"])
