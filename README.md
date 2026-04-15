# Agentic SOTA Examples

State-of-the-art portfolio monorepo with eight connected LangGraph projects. All projects follow a shared orchestration contract and produce standard run artifacts.

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
