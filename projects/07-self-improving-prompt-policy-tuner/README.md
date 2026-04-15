# 07-self-improving-prompt-policy-tuner

Self-improving loop that proposes and evaluates prompt policy updates.

Architecture:

```mermaid
flowchart TD
  mine[MineFailedRuns] --> propose[ProposePatch]
  propose --> benchmark[BenchmarkCandidate]
  benchmark --> gate{ImprovementSignificant}
  gate -->|No| retry[RetryProposal]
  retry --> propose
  gate -->|Yes| emit[EmitRecommendationPackage]
```

Public data source:
- HuggingFace datasets API

Expected outputs:
- standard artifacts + recommendation package json

Run:

```bash
python run_project.py --project 07-self-improving-prompt-policy-tuner
```
