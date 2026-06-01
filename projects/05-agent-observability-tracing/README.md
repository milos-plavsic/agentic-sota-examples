# 05-agent-observability-tracing

Observability-first agent with confidence trajectory and trace outputs.

Architecture:

```mermaid
flowchart TD
  fetch[FetchTelemetryContext] --> propose[ProposeAction]
  propose --> eval[Evaluate]
  eval --> trace[EmitTraceEvent]
  trace --> route{Continue}
  route -->|Yes| propose
  route -->|No| finalize[Finalize]
```

Public data source:
- GitHub public API (`opentelemetry-python` metadata)

Expected outputs:
- standard artifacts with detailed trace file

Run:

```bash
python run_project.py --project 05-agent-observability-tracing
```
