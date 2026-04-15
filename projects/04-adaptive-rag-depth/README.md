# 04-adaptive-rag-depth

Adaptive RAG depth example with dynamic retrieval effort.

Architecture:

```mermaid
flowchart TD
  fetch[FetchContext] --> retrieve[RetrieveTopK]
  retrieve --> expand[ExpandQueryIfNeeded]
  expand --> evaluate[EvaluateCitationSupport]
  evaluate --> loop{NeedMoreDepth}
  loop -->|Yes| retrieve
  loop -->|No| finalize[Finalize]
```

Public data source:
- Wikipedia summary API

Expected outputs:
- standard artifacts with loop history showing depth retries

Run:

```bash
python run_project.py --project 04-adaptive-rag-depth
```
