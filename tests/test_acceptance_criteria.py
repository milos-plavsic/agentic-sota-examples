from __future__ import annotations

from pathlib import Path

from run_project import run_project
from shared.testing import PROJECTS


def test_plan_acceptance_criteria_end_to_end() -> None:
    outputs = [run_project(project) for project in PROJECTS]
    assert len(outputs) == 8

    for out in outputs:
        assert isinstance(out["project"], str) and out["project"]
        assert 0.0 <= float(out["confidence_score"]) <= 1.0
        assert out["confidence_label"] in {"low", "medium", "high"}
        assert out["loop_terminated_reason"] in {
            "confidence_threshold_reached",
            "max_iterations_reached",
            "retry_with_additional_information",
        }
        for key in ("summary_path", "report_path", "trace_path"):
            p = Path(str(out[key]))
            assert p.exists()
            assert p.stat().st_size > 0

    # Acceptance resilience criterion: at least one run must succeed with fallback enabled.
    assert any(bool(out["used_fallback"]) for out in outputs)
