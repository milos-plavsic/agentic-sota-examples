# Runbook

## Local Run

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
make test
make lint
make typecheck
make run PROJECT=01-eval-driven-agent
make report
make real-benchmarks
make benchmark-summary
```

## CI Expectations

- PR CI:
  - runs lint + typecheck gates
  - runs strict smoke quality gates (contract/fallback/schema checks)
  - runs deterministic keyless e2e matrix for all 8 projects
- Nightly CI:
  - runs extended test set
  - generates all reports + benchmark index artifact
  - optionally runs provider-enabled subset if secrets exist
- Scheduled summary refresh:
  - benchmark-summary workflow opens an automated PR with refreshed benchmark markdown

## Troubleshooting

- If internet endpoint is flaky:
  - adapters should fallback to deterministic fixture
  - verify `used_fallback=true` in summary JSON
- If contract test fails:
  - compare output against `shared/orchestration_contract/CONTRACT.md`
