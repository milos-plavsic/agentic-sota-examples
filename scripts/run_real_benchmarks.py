from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from run_project import run_project_with_config


def main() -> None:
    root = ROOT
    inputs_dir = root / "benchmarks" / "inputs"
    out_dir = root / "reports" / "benchmarks"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    for path in sorted(inputs_dir.glob("*.json")):
        project = path.stem
        overrides = json.loads(path.read_text(encoding="utf-8"))
        result = run_project_with_config(project, overrides)
        rows.append(
            {
                "project": result["project"],
                "confidence_score": result["confidence_score"],
                "iterations": result["iterations"],
                "loop_terminated_reason": result["loop_terminated_reason"],
                "used_fallback": result["used_fallback"],
                "source": result["source"],
            }
        )

    (out_dir / "real-benchmark-results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps({"count": len(rows), "output": str(out_dir / "real-benchmark-results.json")}, indent=2))


if __name__ == "__main__":
    main()
