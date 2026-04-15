# Agentic SOTA Examples

State-of-the-art portfolio monorepo with eight connected LangGraph projects. All projects follow a shared orchestration contract and produce standard run artifacts.

[![CI](https://github.com/milos-plavsic/agentic-sota-examples/actions/workflows/ci.yml/badge.svg)](https://github.com/milos-plavsic/agentic-sota-examples/actions/workflows/ci.yml)
[![Nightly](https://github.com/milos-plavsic/agentic-sota-examples/actions/workflows/nightly.yml/badge.svg)](https://github.com/milos-plavsic/agentic-sota-examples/actions/workflows/nightly.yml)

## Project Matrix

| Project | Focus | Primary Public Source |
|---|---|---|
| `01-eval-driven-agent` | Eval-gated retry loop | Wikipedia |
| `02-multi-agent-debate-judge` | Debate + judge synthesis | Semantic Scholar |
| `03-human-in-the-loop-review` | Escalation + resume payloads | GitHub public API |
| `04-adaptive-rag-depth` | Dynamic retrieval effort | Wikipedia |
| `05-agent-observability-tracing` | Trace-first operations | GitHub public API |
| `06-guardrail-policy-engine` | Declarative runtime policies | UCI API |
| `07-self-improving-prompt-policy-tuner` | Patch recommendation loop | HuggingFace datasets API |
| `08-cost-quality-model-router` | Tiered model routing | Wikipedia |

## Quickstart

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
make test
make run PROJECT=01-eval-driven-agent
```

## Demo Shortcuts

- Benchmark snapshot: `docs/LATEST_BENCHMARK_SUMMARY.md`
- Repo architecture: `docs/ARCHITECTURE.md`
- Operational runbook: `docs/RUNBOOK.md`
- Portfolio landing: `docs/PORTFOLIO.md`
- 2-3 min demo plan: `docs/DEMO_SCRIPT.md`
- Portfolio landing: `docs/PORTFOLIO.md`
- 2-3 min demo plan: `docs/DEMO_SCRIPT.md`

## Shared Design

- Contract: `shared/orchestration_contract/CONTRACT.md`
- Confidence policy: `shared/orchestration_policy/policy.py`
- Evals: `shared/evals.py`
- Data adapters: `shared/data_sources/`
- Telemetry traces: `shared/telemetry.py`

## Run Artifacts

Each run emits:
- `reports/<project>-summary.json`
- `reports/<project>-REPORT.md`
- `reports/traces/<project>-trace.json`

## CI Strategy

- PR CI (`.github/workflows/ci.yml`): strict smoke quality gates plus keyless deterministic e2e matrix for all eight projects.
- Nightly CI (`.github/workflows/nightly.yml`): full keyless benchmark run and optional provider-enabled matrix when secrets are present.
- Scheduled benchmark PR workflow (`.github/workflows/benchmark-summary-pr.yml`): refreshes benchmark summary via automated pull request.
- Scheduled benchmark PR workflow (`.github/workflows/benchmark-summary-pr.yml`): refreshes benchmark summary via automated pull request.
