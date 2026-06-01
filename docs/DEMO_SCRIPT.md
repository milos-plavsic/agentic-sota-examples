# Demo Script (2-3 minutes)

## Demo 1: CI reliability

1. Open Actions tab and show latest successful `CI` run.
2. Highlight lint/type/smoke/e2e matrix jobs.
3. Open one `ci-*.json` artifact to show deterministic output payload.

## Demo 2: Nightly benchmark flow

1. Open latest successful `Nightly` run.
2. Show `nightly-results` artifact.
3. Show generated `docs/LATEST_BENCHMARK_SUMMARY.md`.

## Demo 3: End-to-end local run

```bash
make test
make run PROJECT=03-human-in-the-loop-review
make real-benchmarks
make benchmark-summary
```

Discuss:
- confidence loop behavior
- stop reason semantics
- fallback resiliency under source outages
