# 02-multi-agent-debate-judge

Multi-agent debate with judge-based synthesis and confidence scoring.

Architecture:

```mermaid
flowchart TD
  source[FetchResearchContext] --> analyst[Analyst]
  source --> skeptic[Skeptic]
  analyst --> judge[Judge]
  skeptic --> judge
  judge --> decide{ConfidenceHigh}
  decide -->|No| retry[DebateRetry]
  retry --> analyst
  decide -->|Yes| finalize[Finalize]
```

Public data source:
- Semantic Scholar Graph API

Expected outputs:
- standardized summary/report/trace artifacts

Run:

```bash
python run_project.py --project 02-multi-agent-debate-judge
```
