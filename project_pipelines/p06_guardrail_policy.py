from __future__ import annotations

from shared.data_sources import fetch_uci_dataset_note
from shared.guardrails import enforce_policy, redact_sensitive
from shared.runtime import RunState, run_graph


def _proposer(state: RunState) -> str:
    allowed, reason = enforce_policy("internet_fetch", retries=int(state["iteration"]) - 1)
    return (
        "Guardrail policy execution: validate allowed tools, redact sensitive inputs, "
        f"and enforce max retry budget (iteration={state['iteration']}, allowed={allowed}, reason={reason})."
    )


def run(cfg: dict[str, object]) -> dict[str, object]:
    cfg = {**cfg, "topic": "student performance"}
    result = run_graph(
        cfg=cfg,
        source_fetcher=lambda name: fetch_uci_dataset_note(name).__dict__,
        proposer=_proposer,
        estimated_cost_usd=0.0008,
    )
    result["answer"] = redact_sensitive(str(result["answer"]))
    return result
