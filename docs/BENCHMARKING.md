# Benchmarking

## Metrics

- `confidence_score`
- `iterations`
- `loop_terminated_reason`
- `used_fallback`

## Baseline Commands

```bash
make report
python3 - <<'PY'
import json
from pathlib import Path
for p in sorted(Path("reports").glob("*-summary.json")):
    d = json.loads(p.read_text())
    print(d["project"], d["confidence_score"], d["iterations"], d["used_fallback"])
PY
```

## Nightly Artifact

- Nightly workflow writes `reports/nightly-benchmark.json`.
- Upload includes all reports and traces for portfolio evidence.
