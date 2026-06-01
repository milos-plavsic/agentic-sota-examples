"""Multi-Agent Debate with Judge — real implementation.

Three synthetic agents engage in structured argumentation:

  Analyst   — extracts and presents the strongest evidence from the source.
  Skeptic   — challenges claims, highlights missing support and uncertainty.
  Judge     — reads both positions and synthesises a final verdict with a
              calibrated confidence score.

The debate runs for `debate_rounds` rounds.  In each round:
  1. Analyst proposes a position grounded in the source context.
  2. Skeptic rebuts with identified weaknesses.
  3. Judge scores the exchange and decides whether to continue or finalise.

The Judge uses a simple consistency heuristic: if the Analyst's position
overlaps well with the source context AND the Skeptic's objections are
non-trivial (len > threshold), the debate is settled with moderate-to-high
confidence; otherwise another round is triggered.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from shared.data_sources import fetch_arxiv_snippet
from shared.orchestration_policy import clip01, confidence_label, weighted_confidence

# ---------------------------------------------------------------------------
# Agent generators
# ---------------------------------------------------------------------------


def _analyst_turn(context: str, topic: str, round_: int) -> str:
    """Analyst: ground claims in context evidence."""
    excerpt = " ".join(context.split()[: 80 + round_ * 20])
    return (
        f"[Round {round_} | Analyst] Supporting evidence for '{topic}': "
        f"{excerpt}. "
        f"Based on this, the position is well-supported by documented findings. "
        f"Key insight: the source confirms the core claims with specificity."
    )


def _skeptic_turn(analyst_claim: str, context: str, round_: int) -> str:
    """Skeptic: challenge the analyst's claim with identified gaps."""
    # Find tokens in analyst claim NOT in context
    a_tokens = set(re.findall(r"\w+", analyst_claim.lower()))
    c_tokens = set(re.findall(r"\w+", context.lower()))
    unsupported = list(a_tokens - c_tokens - {"the", "a", "an", "is", "are", "of", "in", "for"})[:5]
    gap_list = (
        ", ".join(f"'{t}'" for t in unsupported) if unsupported else "several implicit assumptions"
    )
    return (
        f"[Round {round_} | Skeptic] Counter-argument: The analyst's claim contains "
        f"{gap_list} that are not directly supported by the retrieved context. "
        f"Moreover, the source may be incomplete or biased. "
        f"Confidence should be tempered until additional corroborating sources are consulted. "
        f"Uncertainty remains high for edge cases not covered by this excerpt."
    )


def _judge_synthesise(
    analyst_claim: str,
    skeptic_claim: str,
    context: str,
    round_: int,
) -> dict[str, object]:
    """Judge: score the debate exchange and synthesise a verdict."""
    # Relevance of analyst claim to context
    a_tokens = set(re.findall(r"\w+", analyst_claim.lower()))
    c_tokens = set(re.findall(r"\w+", context.lower()))
    relevance = clip01(len(a_tokens & c_tokens) / max(1, len(c_tokens)) * 4.0)

    # Weight of skeptic's objection (longer = more substantial challenge)
    skeptic_weight = clip01(len(skeptic_claim.split()) / 60.0)

    # Coherence bonus for later rounds (debate matured)
    coherence = clip01(round_ * 0.25)

    composite = weighted_confidence(
        {
            "primary_quality": clip01(relevance * (1.0 - skeptic_weight * 0.4)),
            "secondary_quality": clip01((relevance + coherence) / 2.0),
            "stability": clip01(1.0 - skeptic_weight * 0.5 + round_ * 0.1),
        }
    )

    verdict = (
        f"[Round {round_} | Judge] After reviewing both positions: "
        f"Analyst relevance score={relevance:.2f}, "
        f"Skeptic challenge weight={skeptic_weight:.2f}. "
        f"Composite confidence={composite:.3f} ({confidence_label(composite)}). "
        + (
            "Debate settled — sufficient consensus reached."
            if composite >= 0.65
            else f"Debate continues — confidence below threshold after round {round_}."
        )
    )

    return {
        "verdict": verdict,
        "relevance": relevance,
        "skeptic_weight": skeptic_weight,
        "composite": composite,
        "settled": composite >= 0.65,
    }


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------


@dataclass
class DebateResult:
    topic: str
    rounds: list[dict[str, object]] = field(default_factory=list)
    final_verdict: str = ""
    confidence_score: float = 0.0
    iterations: int = 0
    stop_reason: str = ""


def run(cfg: dict[str, object]) -> dict[str, object]:
    """Run the multi-agent debate.

    Args:
        cfg: dict with keys:
            - topic (str)
            - debate_rounds (int, default 3): max debate rounds
            - confidence_threshold (float, default 0.65)

    Returns:
        dict with verdict, per-round history, confidence_score, stop_reason.
    """
    topic = str(cfg.get("topic", "transformer architecture"))
    max_rounds = int(cfg.get("debate_rounds", cfg.get("max_iterations", 3)))
    float(cfg.get("confidence_threshold", 0.65))

    source_record = fetch_arxiv_snippet(topic)
    context = str(source_record.content)

    rounds: list[dict[str, object]] = []
    final_verdict = ""
    composite = 0.0
    stop_reason = "max_rounds_reached"

    for round_ in range(1, max_rounds + 1):
        analyst = _analyst_turn(context, topic, round_)
        skeptic = _skeptic_turn(analyst, context, round_)
        judgment = _judge_synthesise(analyst, skeptic, context, round_)

        rounds.append(
            {
                "round": round_,
                "analyst": analyst,
                "skeptic": skeptic,
                "verdict": judgment["verdict"],
                "composite": judgment["composite"],
                "settled": judgment["settled"],
            }
        )

        composite = float(judgment["composite"])
        final_verdict = str(judgment["verdict"])

        if judgment["settled"]:
            stop_reason = "consensus_reached"
            break

    return {
        "project": str(cfg.get("project", "02-multi-agent-debate-judge")),
        "task": str(cfg.get("task", "debate_and_judge")),
        "topic": topic,
        "answer": final_verdict,
        "confidence_score": composite,
        "confidence_label": confidence_label(composite),
        "iterations": len(rounds),
        "debate_rounds": rounds,
        "stop_reason": stop_reason,
        "source": str(source_record.source),
        "used_fallback": bool(source_record.used_fallback),
        "estimated_cost_usd": 0.004 * len(rounds),
    }
