from __future__ import annotations

from collections.abc import Mapping
from typing import TypedDict


class LoopDecision(TypedDict):
    continue_loop: bool
    stop_reason: str


def clip01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


def confidence_label(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.6:
        return "medium"
    return "low"


def weighted_confidence(components: Mapping[str, float]) -> float:
    weights = {"primary_quality": 0.55, "secondary_quality": 0.30, "stability": 0.15}
    total = sum(weights.values())
    score = 0.0
    for k, w in weights.items():
        score += w * clip01(float(components.get(k, 0.0)))
    return clip01(score / total)


def decide_loop(
    *,
    confidence_score: float,
    confidence_threshold: float,
    iteration: int,
    max_iterations: int,
) -> LoopDecision:
    reached_conf = float(confidence_score) >= clip01(float(confidence_threshold))
    reached_limit = int(iteration) >= int(max_iterations)
    if reached_conf:
        return {"continue_loop": False, "stop_reason": "confidence_threshold_reached"}
    if reached_limit:
        return {"continue_loop": False, "stop_reason": "max_iterations_reached"}
    return {"continue_loop": True, "stop_reason": "retry_with_additional_information"}
