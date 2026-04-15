from __future__ import annotations

import json
from pathlib import Path

from shared.testing import PROJECTS


def test_real_benchmark_inputs_exist_for_all_projects() -> None:
    root = Path(__file__).resolve().parents[1]
    inputs = root / "benchmarks" / "inputs"
    files = {p.stem: p for p in inputs.glob("*.json")}
    assert set(PROJECTS) == set(files.keys())

    for project in PROJECTS:
        data = json.loads(files[project].read_text(encoding="utf-8"))
        assert isinstance(data.get("task"), str) and data["task"]
        assert isinstance(data.get("topic"), str) and data["topic"]
        assert 0.0 < float(data.get("confidence_threshold", 0.0)) <= 1.0
        assert int(data.get("max_iterations", 0)) >= 1
