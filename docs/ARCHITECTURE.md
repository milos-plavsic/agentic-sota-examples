# Architecture

This monorepo implements a shared runtime for eight specialized LangGraph agent workflows.

```mermaid
flowchart TD
  subgraph shared [SharedLayer]
    contract[Contract]
    policy[ConfidencePolicy]
    evals[Evals]
    sources[DataSources]
    runtime[Runtime]
    telemetry[Telemetry]
    guardrails[Guardrails]
  end

  subgraph projects [ProjectPipelines]
    p1[P01EvalDriven]
    p2[P02DebateJudge]
    p3[P03HumanReview]
    p4[P04AdaptiveRag]
    p5[P05Observability]
    p6[P06GuardrailEngine]
    p7[P07SelfImprover]
    p8[P08CostQualityRouter]
  end

  contract --> runtime
  policy --> runtime
  evals --> runtime
  sources --> runtime
  telemetry --> runtime
  guardrails --> p6
  runtime --> projects
```

## Key modules

- Contract: `shared/orchestration_contract/CONTRACT.md`
- Policy: `shared/orchestration_policy/policy.py`
- Data adapters: `shared/data_sources/`
- Runtime orchestration: `shared/runtime.py`
- Project dispatch: `run_project.py` + `project_pipelines/`
