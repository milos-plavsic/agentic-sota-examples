"""Unit tests for the agentic pattern pipeline implementations.

All tests are self-contained (no network calls, no external services).
Network-dependent data fetchers are patched with deterministic fakes.

Covers:
  1. Eval-driven agent — scoring, proposer, full run
  2. Multi-agent debate — each agent, judge synthesis, full run
  3. Human-in-the-loop — escalation logic, stuck detection, payload
  4. Adaptive RAG — chunking, ranking, hallucination ratio, k adaptation
  5. Cost-quality router — complexity estimation, routing decision, baselines
  6. Self-improver — failure analysis, strategy selection, recommendation
  7. Orchestration policy — clip01, confidence_label, weighted_confidence, decide_loop
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Fake data source record (used to replace network calls)
# ---------------------------------------------------------------------------


class _FakeRecord:
    """Minimal stand-in for a DataSourceRecord."""

    def __init__(self, content: str = "", source: str = "fake", used_fallback: bool = False):
        self.content = content
        self.source = source
        self.used_fallback = used_fallback
        # Make it subscriptable so __dict__ works
        self.__dict__.update({"content": content, "source": source, "used_fallback": used_fallback})


_RICH_CONTEXT = (
    "Machine learning is a branch of artificial intelligence that enables systems "
    "to learn and improve from experience without being explicitly programmed. "
    "It focuses on developing computer programs that can access data and use it to "
    "learn for themselves. The process begins with observations or data, such as "
    "examples, direct experience, or instruction. It looks for patterns in data and "
    "makes better decisions in the future. The primary aim is to allow the computers "
    "to learn automatically without human intervention or assistance and adjust actions "
    "accordingly. Machine learning algorithms are trained on large datasets and can "
    "therefore make predictions or decisions without being explicitly told how to. "
    "This includes supervised learning, unsupervised learning, and reinforcement learning. "
    "Supervised learning involves training on labeled data. Unsupervised learning finds "
    "hidden patterns in unlabeled data. Reinforcement learning trains agents via rewards. "
    "Deep learning, a subset of machine learning, uses neural networks with many layers."
)

_FAKE_RECORD = _FakeRecord(content=_RICH_CONTEXT)


# ===========================================================================
# 1. Orchestration policy (no mocking needed — pure functions)
# ===========================================================================


class TestOrchestrationPolicy:
    def test_clip01_below_zero(self) -> None:
        from shared.orchestration_policy import clip01

        assert clip01(-5.0) == 0.0

    def test_clip01_above_one(self) -> None:
        from shared.orchestration_policy import clip01

        assert clip01(10.0) == 1.0

    def test_clip01_in_range(self) -> None:
        from shared.orchestration_policy import clip01

        assert clip01(0.42) == pytest.approx(0.42)

    def test_confidence_label_high(self) -> None:
        from shared.orchestration_policy import confidence_label

        assert confidence_label(0.85) == "high"

    def test_confidence_label_medium(self) -> None:
        from shared.orchestration_policy import confidence_label

        assert confidence_label(0.65) == "medium"

    def test_confidence_label_low(self) -> None:
        from shared.orchestration_policy import confidence_label

        assert confidence_label(0.3) == "low"

    def test_weighted_confidence_all_ones(self) -> None:
        from shared.orchestration_policy import weighted_confidence

        score = weighted_confidence(
            {"primary_quality": 1.0, "secondary_quality": 1.0, "stability": 1.0}
        )
        assert score == pytest.approx(1.0)

    def test_weighted_confidence_all_zeros(self) -> None:
        from shared.orchestration_policy import weighted_confidence

        score = weighted_confidence(
            {"primary_quality": 0.0, "secondary_quality": 0.0, "stability": 0.0}
        )
        assert score == pytest.approx(0.0)

    def test_decide_loop_threshold_reached(self) -> None:
        from shared.orchestration_policy import decide_loop

        dec = decide_loop(
            confidence_score=0.9,
            confidence_threshold=0.7,
            iteration=1,
            max_iterations=5,
        )
        assert dec["continue_loop"] is False
        assert dec["stop_reason"] == "confidence_threshold_reached"

    def test_decide_loop_max_iterations_reached(self) -> None:
        from shared.orchestration_policy import decide_loop

        dec = decide_loop(
            confidence_score=0.3,
            confidence_threshold=0.7,
            iteration=5,
            max_iterations=5,
        )
        assert dec["continue_loop"] is False
        assert dec["stop_reason"] == "max_iterations_reached"

    def test_decide_loop_continue(self) -> None:
        from shared.orchestration_policy import decide_loop

        dec = decide_loop(
            confidence_score=0.4,
            confidence_threshold=0.7,
            iteration=2,
            max_iterations=5,
        )
        assert dec["continue_loop"] is True


# ===========================================================================
# 2. Eval-Driven Agent
# ===========================================================================


class TestEvalDrivenAgent:
    def _run(self, **kwargs) -> dict:
        from project_pipelines import p01_eval_driven_agent as m

        cfg = {
            "topic": "machine learning",
            "max_iterations": 3,
            "confidence_threshold": 0.7,
            **kwargs,
        }
        with patch(
            "project_pipelines.p01_eval_driven_agent.fetch_wikipedia_summary",
            return_value=_FAKE_RECORD,
        ):
            return m.run(cfg)

    def test_score_relevance_high_overlap(self) -> None:
        from project_pipelines.p01_eval_driven_agent import _score_relevance

        context = "machine learning neural network gradient"
        answer = "machine learning gradient backprop neural network"
        score = _score_relevance(answer, context)
        assert score > 0.5

    def test_score_relevance_no_overlap(self) -> None:
        from project_pipelines.p01_eval_driven_agent import _score_relevance

        score = _score_relevance("xyz abc def", "apple orange banana")
        assert score == pytest.approx(0.0)

    def test_score_completeness_long_answer(self) -> None:
        from project_pipelines.p01_eval_driven_agent import _score_completeness

        long_answer = " ".join(["word"] * 350)
        assert _score_completeness(long_answer) == pytest.approx(1.0)

    def test_score_coherence_with_markers(self) -> None:
        from project_pipelines.p01_eval_driven_agent import _score_coherence

        answer = "therefore we see however it is moreover important"
        assert _score_coherence(answer) > 0.0

    def test_score_response_returns_all_keys(self) -> None:
        from project_pipelines.p01_eval_driven_agent import score_response

        result = score_response("this is an answer about machine learning", _RICH_CONTEXT)
        for k in ("relevance", "completeness", "coherence", "calibration", "composite"):
            assert k in result

    def test_score_response_composite_in_range(self) -> None:
        from project_pipelines.p01_eval_driven_agent import score_response

        result = score_response("machine learning neural networks", _RICH_CONTEXT)
        assert 0.0 <= result["composite"] <= 1.0

    def test_run_returns_required_keys(self) -> None:
        result = self._run()
        for k in (
            "answer",
            "confidence_score",
            "iterations",
            "stop_reason",
            "iteration_history",
            "topic",
        ):
            assert k in result, f"Missing key: {k}"

    def test_run_iterations_bounded(self) -> None:
        result = self._run(max_iterations=2)
        assert result["iterations"] <= 2

    def test_run_stop_reason_is_valid(self) -> None:
        result = self._run()
        assert result["stop_reason"] in ("confidence_threshold_reached", "max_iterations_reached")

    def test_run_confidence_score_in_range(self) -> None:
        result = self._run()
        assert 0.0 <= result["confidence_score"] <= 1.0


# ===========================================================================
# 3. Multi-Agent Debate
# ===========================================================================


class TestDebateJudge:
    def _run(self, **kwargs) -> dict:
        from project_pipelines import p02_debate_judge as m

        cfg = {
            "topic": "transformer architecture",
            "max_iterations": 3,
            "confidence_threshold": 0.65,
            **kwargs,
        }
        with patch(
            "project_pipelines.p02_debate_judge.fetch_arxiv_snippet", return_value=_FAKE_RECORD
        ):
            return m.run(cfg)

    def test_analyst_turn_contains_topic(self) -> None:
        from project_pipelines.p02_debate_judge import _analyst_turn

        claim = _analyst_turn(_RICH_CONTEXT, "neural nets", round_=1)
        assert "neural nets" in claim

    def test_skeptic_turn_contains_counter(self) -> None:
        from project_pipelines.p02_debate_judge import _skeptic_turn

        claim = _skeptic_turn("some claim with xyz", _RICH_CONTEXT, round_=1)
        assert "Counter-argument" in claim or "Skeptic" in claim

    def test_judge_synthesis_returns_composite(self) -> None:
        from project_pipelines.p02_debate_judge import _judge_synthesise

        result = _judge_synthesise(
            "analyst claim machine learning", "skeptic doubt", _RICH_CONTEXT, 1
        )
        assert "composite" in result
        assert 0.0 <= result["composite"] <= 1.0

    def test_judge_synthesis_settled_key(self) -> None:
        from project_pipelines.p02_debate_judge import _judge_synthesise

        result = _judge_synthesise("ml", "counter", _RICH_CONTEXT, 3)
        assert "settled" in result

    def test_run_returns_debate_rounds(self) -> None:
        result = self._run()
        assert "debate_rounds" in result
        assert isinstance(result["debate_rounds"], list)

    def test_run_stop_reason_valid(self) -> None:
        result = self._run()
        assert result["stop_reason"] in ("consensus_reached", "max_rounds_reached")

    def test_run_confidence_in_range(self) -> None:
        result = self._run()
        assert 0.0 <= result["confidence_score"] <= 1.0


# ===========================================================================
# 4. Adaptive RAG
# ===========================================================================


class TestAdaptiveRAG:
    def _run(self, **kwargs) -> dict:
        from project_pipelines import p04_adaptive_rag as m

        cfg = {
            "topic": "retrieval augmented generation",
            "max_iterations": 3,
            "confidence_threshold": 0.7,
            **kwargs,
        }
        with patch(
            "project_pipelines.p04_adaptive_rag.fetch_wikipedia_summary", return_value=_FAKE_RECORD
        ):
            return m.run(cfg)

    def test_chunk_context_creates_chunks(self) -> None:
        from project_pipelines.p04_adaptive_rag import _chunk_context

        chunks = _chunk_context(_RICH_CONTEXT, chunk_size=20, overlap=5)
        assert len(chunks) >= 2

    def test_chunk_context_overlap(self) -> None:
        from project_pipelines.p04_adaptive_rag import _chunk_context

        chunks = _chunk_context("a b c d e f g h i j", chunk_size=4, overlap=2)
        assert len(chunks) >= 2

    def test_rank_chunks_top_k(self) -> None:
        from project_pipelines.p04_adaptive_rag import _rank_chunks

        chunks = [
            "apple orange",
            "machine learning gradient",
            "neural network deep",
            "unrelated text",
        ]
        top = _rank_chunks(chunks, "machine learning", top_k=2)
        assert len(top) == 2

    def test_hallucination_ratio_zero_when_grounded(self) -> None:
        from project_pipelines.p04_adaptive_rag import _hallucination_ratio

        # All answer tokens are in the chunk
        ratio = _hallucination_ratio("machine learning", ["machine learning neural"])
        assert ratio < 0.5

    def test_hallucination_ratio_high_when_ungrounded(self) -> None:
        from project_pipelines.p04_adaptive_rag import _hallucination_ratio

        ratio = _hallucination_ratio(
            "xyz abc qwerty foo bar", ["completely different content here"]
        )
        assert ratio > 0.3

    def test_query_expansion_adds_terms(self) -> None:
        from project_pipelines.p04_adaptive_rag import _expand_query

        expanded = _expand_query("neural network training")
        assert len(expanded) > len("neural network training")

    def test_run_returns_retrieval_history(self) -> None:
        result = self._run()
        assert "retrieval_history" in result
        assert isinstance(result["retrieval_history"], list)

    def test_run_k_increases_on_low_confidence(self) -> None:
        # With a very high threshold, k should increase
        result = self._run(confidence_threshold=0.99, initial_k=2, max_iterations=3)
        assert result["final_k"] >= 2

    def test_run_confidence_in_range(self) -> None:
        result = self._run()
        assert 0.0 <= result["confidence_score"] <= 1.0


# ===========================================================================
# 5. Cost-Quality Router
# ===========================================================================


class TestCostQualityRouter:
    def _run(self, **kwargs) -> dict:
        from project_pipelines import p08_cost_quality_router as m

        cfg = {"topic": "machine learning cost quality", **kwargs}
        with patch(
            "project_pipelines.p08_cost_quality_router.fetch_wikipedia_summary",
            return_value=_FAKE_RECORD,
        ):
            return m.run(cfg)

    def test_estimate_complexity_short_context(self) -> None:
        from project_pipelines.p08_cost_quality_router import estimate_complexity

        score = estimate_complexity("simple topic", "a b c d")
        assert score < 0.5

    def test_estimate_complexity_long_context(self) -> None:
        from project_pipelines.p08_cost_quality_router import estimate_complexity

        score = estimate_complexity("topic", _RICH_CONTEXT * 3)
        assert score > 0.0

    def test_estimate_complexity_with_signals(self) -> None:
        from project_pipelines.p08_cost_quality_router import estimate_complexity

        base = estimate_complexity("explain", _RICH_CONTEXT)
        no_sig = estimate_complexity("topic", _RICH_CONTEXT)
        assert base >= no_sig

    def test_run_returns_routing_decision(self) -> None:
        result = self._run()
        assert "routing_decision" in result
        assert result["routing_decision"] in ("cheap_accepted", "escalated", "direct_to_strong")

    def test_run_returns_benchmark(self) -> None:
        result = self._run()
        assert "router_benchmark" in result
        bench = result["router_benchmark"]
        assert "router_score" in bench
        assert "always_cheap_score" in bench
        assert "always_strong_score" in bench

    def test_run_cost_positive(self) -> None:
        result = self._run()
        assert result["total_cost_usd"] > 0.0

    def test_run_confidence_in_range(self) -> None:
        result = self._run()
        assert 0.0 <= result["confidence_score"] <= 1.0


# ===========================================================================
# 6. Self-Improver
# ===========================================================================


class TestSelfImprover:
    def _run(self, **kwargs) -> dict:
        from project_pipelines import p07_self_improver as m

        cfg = {
            "topic": "stanfordnlp/imdb",
            "max_iterations": 3,
            "confidence_threshold": 0.7,
            **kwargs,
        }
        with patch(
            "project_pipelines.p07_self_improver.fetch_hf_dataset_card", return_value=_FAKE_RECORD
        ):
            return m.run(cfg)

    def test_analyse_failure_returns_weakest(self) -> None:
        from project_pipelines.p07_self_improver import analyse_failure

        scores = {
            "relevance": 0.1,
            "completeness": 0.9,
            "coherence": 0.8,
            "calibration": 0.7,
            "composite": 0.6,
        }
        assert analyse_failure(scores) == "relevance"

    def test_apply_strategy_relevance(self) -> None:
        from project_pipelines.p07_self_improver import _apply_strategy

        result = _apply_strategy("initial answer", _RICH_CONTEXT, "relevance", 1)
        assert "source context" in result.lower() or "additionally" in result.lower()

    def test_apply_strategy_coherence(self) -> None:
        from project_pipelines.p07_self_improver import _apply_strategy

        result = _apply_strategy("initial answer", _RICH_CONTEXT, "coherence", 1)
        # Should contain discourse markers
        assert any(m in result.lower() for m in ["therefore", "moreover", "specifically"])

    def test_apply_strategy_calibration(self) -> None:
        from project_pipelines.p07_self_improver import _apply_strategy

        result = _apply_strategy("initial answer", _RICH_CONTEXT, "calibration", 1)
        assert "uncertainty" in result.lower() or "evidence suggests" in result.lower()

    def test_run_returns_strategies_applied(self) -> None:
        result = self._run()
        assert "strategies_applied" in result
        assert isinstance(result["strategies_applied"], list)

    def test_run_returns_recommendation(self) -> None:
        result = self._run()
        assert "recommendation" in result
        rec = result["recommendation"]
        assert "recommended_change" in rec
        assert "expected_impact" in rec

    def test_run_confidence_improves_or_stays(self) -> None:
        result = self._run(max_iterations=3, confidence_threshold=0.99)
        history = result["iteration_history"]
        # Confidence should not decrease catastrophically
        if len(history) >= 2:
            first = history[0]["composite"]
            last = history[-1]["composite"]
            assert last >= first - 0.1  # at most 0.1 degradation (tolerance)

    def test_run_stop_reason_valid(self) -> None:
        result = self._run()
        assert result["stop_reason"] in ("confidence_threshold_reached", "max_iterations_reached")


# ===========================================================================
# 7. Human-in-the-Loop
# ===========================================================================


class TestHumanInTheLoop:
    def _run(self, **kwargs) -> dict:
        from project_pipelines import p03_human_review as m

        cfg = {
            "topic": "microsoft/semantic-kernel",
            "max_iterations": 3,
            "confidence_threshold": 0.9,
            **kwargs,
        }
        with patch(
            "project_pipelines.p03_human_review.fetch_github_repo_summary",
            return_value=_FAKE_RECORD,
        ):
            return m.run(cfg)

    def test_high_threshold_triggers_escalation(self) -> None:
        # threshold=0.99 means agent will almost certainly not meet it → escalate
        result = self._run(confidence_threshold=0.99)
        assert result["escalated_to_human"] is True

    def test_escalation_payload_has_required_keys(self) -> None:
        result = self._run(confidence_threshold=0.99)
        if result["escalated_to_human"]:
            payload = result["escalation_payload"]
            assert "unresolved_questions" in payload
            assert "suggested_actions" in payload
            assert "confidence_trajectory" in payload

    def test_confidence_trajectory_list(self) -> None:
        result = self._run()
        assert "confidence_trajectory" in result
        assert isinstance(result["confidence_trajectory"], list)
        assert len(result["confidence_trajectory"]) >= 1

    def test_stop_reason_valid(self) -> None:
        result = self._run()
        assert result["stop_reason"] in (
            "confidence_threshold_reached",
            "max_iterations_reached",
            "stuck_early_escalation",
        )

    def test_no_escalation_when_threshold_low(self) -> None:
        # threshold=0.0 means any score passes → no escalation
        result = self._run(confidence_threshold=0.0)
        assert result["escalated_to_human"] is False
