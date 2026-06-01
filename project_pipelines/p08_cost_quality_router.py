"""Cost-Quality Model Router — real implementation.

Simulates a two-tier model system:
  - cheap_model:  fast, low cost, lower quality ceiling
  - strong_model: slower, higher cost, higher quality ceiling

Routing algorithm:
  1. Estimate query complexity from source context (token count, question type).
  2. If complexity < COMPLEXITY_THRESHOLD → route to cheap_model.
  3. Run cheap_model and score its output.
  4. If cheap_model score >= QUALITY_GATE → accept and return (no escalation).
  5. Otherwise escalate to strong_model and return its result.

Cost tracking:
  - cheap_model:  $0.0005 per call
  - strong_model: $0.004  per call
  Compared against always-cheap and always-strong baselines.

Complexity estimation uses:
  - word count of context (proxy for required depth)
  - presence of "why" / "how" / "compare" / "explain" (complex question signals)
"""

from __future__ import annotations

import re

from shared.data_sources import fetch_wikipedia_summary
from shared.orchestration_policy import clip01, confidence_label, weighted_confidence

# ---------------------------------------------------------------------------
# Model tier definitions
# ---------------------------------------------------------------------------

CHEAP_MODEL_COST = 0.0005
STRONG_MODEL_COST = 0.004
COMPLEXITY_THRESHOLD = 0.5  # 0..1 normalised
QUALITY_GATE = 0.60  # cheap model score threshold before escalation

COMPLEX_QUESTION_SIGNALS = ["why", "how", "explain", "compare", "contrast", "analyse", "evaluate"]


# ---------------------------------------------------------------------------
# Complexity estimation
# ---------------------------------------------------------------------------


def estimate_complexity(topic: str, context: str) -> float:
    """Score query complexity in [0, 1].

    Considers:
      - context length (longer = harder)
      - presence of complex question signals in topic
      - vocabulary diversity of context (type/token ratio)
    """
    word_count = len(context.split())
    length_score = clip01(word_count / 500.0)  # normalised; 500 words → complexity 1.0

    topic_lower = topic.lower()
    signal_hits = sum(1 for sig in COMPLEX_QUESTION_SIGNALS if sig in topic_lower)
    signal_score = clip01(signal_hits / 2.0)

    tokens = re.findall(r"\w+", context.lower())
    type_token_ratio = clip01(len(set(tokens)) / max(1, len(tokens)) * 3.0)

    return clip01((length_score * 0.5) + (signal_score * 0.3) + (type_token_ratio * 0.2))


# ---------------------------------------------------------------------------
# Model simulators
# ---------------------------------------------------------------------------


def _cheap_model_generate(topic: str, context: str) -> str:
    """Short, fast answer with lower quality ceiling."""
    excerpt = " ".join(context.split()[:50])
    return (
        f"Quick answer for '{topic}': {excerpt}. "
        f"Key point: the topic relates to common ML/AI patterns."
    )


def _strong_model_generate(topic: str, context: str) -> str:
    """Detailed, higher-quality answer with discourse structure."""
    excerpt_1 = " ".join(context.split()[:80])
    excerpt_2 = " ".join(context.split()[80:140]) if len(context.split()) > 80 else ""
    return (
        f"Comprehensive analysis of '{topic}': {excerpt_1}. "
        f"Moreover, evidence suggests: {excerpt_2}. "
        f"Therefore, the key mechanisms involve token-level features, "
        f"structural patterns, and contextual relationships. "
        f"Specifically, this is important because it enables higher-quality inference. "
        f"However, limitations remain where context is sparse. "
        f"As a result, confidence is calibrated at the empirical level."
    )


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def _score_answer(answer: str, context: str, cost: float) -> dict[str, float]:
    a_tokens = set(re.findall(r"\w+", answer.lower()))
    c_tokens = set(re.findall(r"\w+", context.lower()))
    relevance = clip01(len(a_tokens & c_tokens) / max(1, len(c_tokens)) * 4.0)
    completeness = clip01(len(answer.split()) / 200.0)
    cost_quality = clip01(1.0 - min(cost, 0.01) / 0.01)
    composite = weighted_confidence(
        {
            "primary_quality": clip01((relevance + completeness) / 2.0),
            "secondary_quality": clip01((completeness + cost_quality) / 2.0),
            "stability": relevance,
        }
    )
    return {
        "relevance": relevance,
        "completeness": completeness,
        "cost_quality": cost_quality,
        "composite": composite,
        "estimated_cost_usd": cost,
    }


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------


def run(cfg: dict[str, object]) -> dict[str, object]:
    """Run the cost-quality router.

    Args:
        cfg: dict with:
            - topic (str)
            - quality_gate (float, default 0.60): min score before escalation
            - complexity_threshold (float, default 0.50): above this, use strong directly
    Returns:
        dict with answer, routing_decision, cost breakdown, confidence_score.
    """
    topic = str(cfg.get("topic", "cost quality tradeoff in machine learning"))
    quality_gate = float(cfg.get("quality_gate", QUALITY_GATE))
    complexity_thresh = float(cfg.get("complexity_threshold", COMPLEXITY_THRESHOLD))

    source_record = fetch_wikipedia_summary(topic)
    context = str(source_record.content)

    complexity = estimate_complexity(topic, context)
    routing_log: list[dict[str, object]] = []
    total_cost = 0.0

    # Step 1: complexity-based pre-routing
    if complexity >= complexity_thresh:
        # Skip cheap model entirely for complex queries
        answer = _strong_model_generate(topic, context)
        cost = STRONG_MODEL_COST
        total_cost += cost
        scores = _score_answer(answer, context, cost)
        routing_log.append(
            {
                "step": "direct_strong",
                "reason": f"complexity={complexity:.3f} >= threshold={complexity_thresh}",
                "model": "strong_model",
                **scores,
            }
        )
        routing_decision = "direct_to_strong"
    else:
        # Step 2: try cheap model first
        answer = _cheap_model_generate(topic, context)
        cost = CHEAP_MODEL_COST
        total_cost += cost
        scores = _score_answer(answer, context, cost)
        routing_log.append(
            {
                "step": "cheap_model",
                "reason": f"complexity={complexity:.3f} < threshold={complexity_thresh}",
                "model": "cheap_model",
                **scores,
            }
        )

        if scores["composite"] >= quality_gate:
            routing_decision = "cheap_accepted"
        else:
            # Step 3: escalate to strong model
            answer = _strong_model_generate(topic, context)
            cost = STRONG_MODEL_COST
            total_cost += cost
            scores = _score_answer(answer, context, cost)
            routing_log.append(
                {
                    "step": "escalated_to_strong",
                    "reason": f"cheap score={routing_log[0]['composite']:.3f} < gate={quality_gate}",
                    "model": "strong_model",
                    **scores,
                }
            )
            routing_decision = "escalated"

    # Baseline comparisons
    cheap_baseline_score = float(
        _score_answer(_cheap_model_generate(topic, context), context, CHEAP_MODEL_COST)["composite"]
    )
    strong_baseline_score = float(
        _score_answer(_strong_model_generate(topic, context), context, STRONG_MODEL_COST)[
            "composite"
        ]
    )

    final_score = float(scores["composite"])

    return {
        "project": str(cfg.get("project", "08-cost-quality-model-router")),
        "task": str(cfg.get("task", "cost_quality_routing")),
        "topic": topic,
        "answer": answer,
        "confidence_score": final_score,
        "confidence_label": confidence_label(final_score),
        "routing_decision": routing_decision,
        "complexity_score": complexity,
        "total_cost_usd": total_cost,
        "routing_log": routing_log,
        "router_benchmark": {
            "router_score": final_score,
            "always_cheap_score": cheap_baseline_score,
            "always_strong_score": strong_baseline_score,
            "cost_savings_vs_always_strong": max(0.0, STRONG_MODEL_COST - total_cost),
        },
        "iterations": len(routing_log),
        "source": str(source_record.source),
        "used_fallback": bool(source_record.used_fallback),
        "estimated_cost_usd": total_cost,
    }
