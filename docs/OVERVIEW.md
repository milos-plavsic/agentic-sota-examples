# Repository overview

## What this repository demonstrates

- End-to-end agent engineering with LangGraph across eight project archetypes.
- Shared contract-first orchestration with confidence-gated retries.
- Public internet data integrations with fallback behavior for CI reliability.
- CI/CD maturity: lint, type-check, smoke tests, e2e matrix, nightly benchmark workflows.

## Architecture and execution

- Overview: `docs/ARCHITECTURE.md`
- Runbook: `docs/RUNBOOK.md`
- Benchmark snapshot: `docs/LATEST_BENCHMARK_SUMMARY.md`

## Evaluation protocol

- Metrics: confidence score, iteration count, stop reason, fallback usage.
- Sources: project-specific public APIs (Wikipedia, GitHub, UCI, HuggingFace, Semantic Scholar).
- Reproducibility:
  - `make test`
  - `make run-all`
  - `make real-benchmarks`
  - `make benchmark-summary`

## Release and evidence

- Stable baseline release: `v0.1.0`
- CI workflow and artifacts are available in repository Actions.
- Nightly workflow exports benchmark artifacts and generated summary markdown.
