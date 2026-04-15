from __future__ import annotations

from pathlib import Path

from run_project import run_project


def test_project_run_writes_required_artifacts() -> None:
    out = run_project("03-human-in-the-loop-review")
    for key in ("summary_path", "report_path", "trace_path"):
        p = Path(str(out[key]))
        assert p.exists()
        assert p.stat().st_size > 0
