from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_policy(path: str | None = None) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    target = Path(path) if path else (root / "policies" / "default.yaml")
    return yaml.safe_load(target.read_text(encoding="utf-8"))


def enforce_policy(action: str, *, retries: int) -> tuple[bool, str]:
    policy = load_policy()
    allowed = set(policy.get("allowed_tools", []))
    max_retries = int(policy.get("max_retries", 3))
    if action not in allowed:
        return False, f"tool_not_allowed:{action}"
    if retries > max_retries:
        return False, "retry_budget_exceeded"
    return True, "ok"


def redact_sensitive(text: str) -> str:
    policy = load_policy()
    output = text
    for token in policy.get("redact_tokens", []):
        output = output.replace(str(token), "***")
    return output
