from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def emit_trace(project: str, events: list[dict[str, Any]]) -> str:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "reports" / "traces"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{project}-trace.json"
    payload = {
        "project": project,
        "generated_at_epoch_s": int(time.time()),
        "events": events,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)
