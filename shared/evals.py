from __future__ import annotations

from typing import TypedDict

from shared.orchestration_policy import clip01, weighted_confidence


class EvalResult(TypedDict):
    primary_quality: float
    secondary_quality: float
    stability: float
    calibration: float
    latency_quality: float
    cost_quality: float
    confidence_score: float


def score_text_answer(
    answer: str,
    source_context: str,
    iteration: int,
    *,
    latency_ms: int = 0,
    estimated_cost_usd: float = 0.0,
) -> EvalResult:
    answer_len = max(1, len(answer))
    overlap_tokens = set(answer.lower().split()) & set(source_context.lower().split())
    overlap_ratio = len(overlap_tokens) / max(1, len(set(source_context.lower().split())))

    primary_quality = clip01(overlap_ratio * 2.0)
    secondary_quality = clip01(min(answer_len / 500.0, 1.0))
    stability = clip01(1.0 - min(iteration, 6) * 0.08)
    calibration = clip01((primary_quality + secondary_quality) / 2.0)
    latency_quality = clip01(1.0 - min(max(latency_ms, 0), 3000) / 3000.0)
    cost_quality = clip01(1.0 - min(max(estimated_cost_usd, 0.0), 0.02) / 0.02)
    confidence = weighted_confidence(
        {
            "primary_quality": (primary_quality + calibration) / 2.0,
            "secondary_quality": (secondary_quality + cost_quality + latency_quality) / 3.0,
            "stability": stability,
        }
    )
    return {
        "primary_quality": primary_quality,
        "secondary_quality": secondary_quality,
        "stability": stability,
        "calibration": calibration,
        "latency_quality": latency_quality,
        "cost_quality": cost_quality,
        "confidence_score": confidence,
    }
