from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_pipelines import PROJECT_RUNNERS

ROOT = Path(__file__).resolve().parent


def _load_config(project_name: str) -> dict[str, object]:
    cfg_path = ROOT / "projects" / project_name / "project.json"
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def run_project_with_config(project_name: str, cfg_overrides: dict[str, object] | None = None) -> dict[str, object]:
    cfg = _load_config(project_name)
    if cfg_overrides:
        cfg.update(cfg_overrides)
    runner = PROJECT_RUNNERS.get(project_name)
    if runner is None:
        raise ValueError(f"Unsupported project name: {project_name}")
    return runner(cfg)


def run_project(project_name: str) -> dict[str, object]:
    return run_project_with_config(project_name)


def main() -> None:
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
