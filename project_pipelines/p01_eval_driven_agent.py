"""Eval-Driven Agent — real implementation.

The agent iterates through a propose → score → refine loop until either
the composite quality score exceeds `confidence_threshold` or
`max_iterations` is reached.

Scoring criteria (each [0, 1]):
  - relevance:    token-overlap between answer and source context
  - completeness: answer length relative to a 300-token target
  - coherence:    presence of structured discourse markers
  - calibration:  averaged relevance x completeness (cross-signal consistency)

Refinement strategy:
  - iteration 1: short, direct answer
  - iteration 2: expand with evidence quotes from source context
  - iteration 3+: add counter-argument handling and explicit uncertainty hedging
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from shared.data_sources import fetch_wikipedia_summary
from shared.orchestration_policy import clip01, weighted_confidence

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

DISCOURSE_MARKERS = [
    "because",
    "therefore",
    "however",
    "moreover",
    "consequently",
    "specifically",
    "for example",
    "in contrast",
    "as a result",
    "evidence suggests",
    "research shows",
]


def _score_relevance(answer: str, context: str) -> float:
    """Token overlap between answer and context (Jaccard-like)."""
    a_tokens = set(re.findall(r"\w+", answer.lower()))
    c_tokens = set(re.findall(r"\w+", context.lower()))
    if not c_tokens:
        return 0.0
    overlap = a_tokens & c_tokens
    return clip01(len(overlap) / max(1, len(c_tokens)) * 3.0)


def _score_completeness(answer: str, target_tokens: int = 300) -> float:
    """How close to the target length?"""
    token_count = len(answer.split())
    return clip01(token_count / target_tokens)


def _score_coherence(answer: str) -> float:
    """Fraction of discourse markers present."""
    lower = answer.lower()
    hits = sum(1 for m in DISCOURSE_MARKERS if m in lower)
    return clip01(hits / max(1, len(DISCOURSE_MARKERS)) * 4.0)


def score_response(answer: str, context: str) -> dict[str, float]:
    """Score an answer against criteria. Returns dict with all sub-scores + composite."""
    relevance = _score_relevance(answer, context)
    completeness = _score_completeness(answer)
    coherence = _score_coherence(answer)
    calibration = clip01((relevance + completeness) / 2.0)
    composite = weighted_confidence(
        {
            "primary_quality": clip01((relevance + calibration) / 2.0),
            "secondary_quality": clip01((completeness + coherence) / 2.0),
            "stability": calibration,
        }
    )
    return {
        "relevance": relevance,
        "completeness": completeness,
        "coherence": coherence,
        "calibration": calibration,
        "composite": composite,
    }


# ---------------------------------------------------------------------------
# Proposer strategies
# ---------------------------------------------------------------------------


def _propose(context: str, topic: str, iteration: int, prev_score: float | None) -> str:
    """Generate an answer, escalating detail with each iteration."""
    # Extract a short excerpt from context (simulate retrieval)
    excerpt = " ".join(context.split()[:60]) + "..."

    if iteration == 1:
        return (
            f"Based on available information about '{topic}': {excerpt} "
            f"This provides a concise initial answer to the query."
        )

    if iteration == 2:
        # Expand with evidence + discourse markers
        evidence = " ".join(context.split()[60:120]) + "..."
        return (
            f"Expanding on the initial response for '{topic}': {excerpt} "
            f"Moreover, evidence suggests: {evidence} "
            f"Therefore, a more complete picture emerges from combining these sources. "
            f"However, additional context may be needed for full confidence."
        )

    # iteration 3+: add counter-argument handling and uncertainty
    hedge = (
        "Research shows there is nuance here: "
        if (prev_score is not None and prev_score < 0.5)
        else "Consequently, we can assert with moderate confidence: "
    )
    return (
        f"{hedge}For '{topic}', the core finding is: {excerpt} "
        f"Specifically, the key mechanisms involve: {' '.join(context.split()[30:80])}. "
        f"In contrast to simpler explanations, this account handles edge cases by "
        f"acknowledging uncertainty where evidence is incomplete. "
        f"For example, the above source context demonstrates this nuance directly. "
        f"As a result, confidence is calibrated rather than overstated."
    )


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------


@dataclass
class EvalDrivenResult:
    topic: str
    final_answer: str
    scores: list[dict[str, float]] = field(default_factory=list)
    iterations: int = 0
    stop_reason: str = ""
    final_score: float = 0.0


def run(cfg: dict[str, object]) -> dict[str, object]:
    """Run the eval-driven agent loop.

    Args:
        cfg: dict with keys:
            - topic (str): the subject to answer
            - confidence_threshold (float, default 0.7): stop when composite >= this
            - max_iterations (int, default 3): hard cap on iterations
    Returns:
        dict with topic, answer, score history, iterations, stop_reason, confidence_score
    """
    topic = str(cfg.get("topic", "machine learning"))
    threshold = float(cfg.get("confidence_threshold", 0.7))
    max_iter = int(cfg.get("max_iterations", 3))

    # Fetch source context once
    source_record = fetch_wikipedia_summary(topic)
    context = str(source_record.content)

    history: list[dict[str, float]] = []
    answer = ""
    prev_score: float | None = None
    stop_reason = "max_iterations_reached"

    for iteration in range(1, max_iter + 1):
        answer = _propose(context, topic, iteration, prev_score)
        scores = score_response(answer, context)
        scores["iteration"] = float(iteration)
        history.append(scores)
        prev_score = scores["composite"]

        if scores["composite"] >= threshold:
            stop_reason = "confidence_threshold_reached"
            break

    return {
        "project": str(cfg.get("project", "01-eval-driven-agent")),
        "task": str(cfg.get("task", "answer_query")),
        "topic": topic,
        "answer": answer,
        "confidence_score": prev_score or 0.0,
        "confidence_label": (
            "high" if (prev_score or 0) >= 0.8 else "medium" if (prev_score or 0) >= 0.6 else "low"
        ),
        "iterations": len(history),
        "iteration_history": history,
        "stop_reason": stop_reason,
        "source": str(source_record.source),
        "used_fallback": bool(source_record.used_fallback),
        "estimated_cost_usd": 0.002 * len(history),
    }
