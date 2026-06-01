# 01-eval-driven-agent

Evaluation-driven agent for evidence-backed answer refinement.

Architecture:

```mermaid
flowchart TD
  ingest[IngestSource] --> propose[ProposeAnswer]
  propose --> evaluate[EvaluateQualityCalibrationCost]
  evaluate --> decide{ThresholdReached}
  decide -->|No| retry[RetryWithMoreContext]
  retry --> propose
  decide -->|Yes| finalize[Finalize]
```

Public data source:
- Wikipedia summary API

Expected outputs:
- summary/report/trace artifacts in `reports/`

Run:

```bash
python run_project.py --project 01-eval-driven-agent
```
