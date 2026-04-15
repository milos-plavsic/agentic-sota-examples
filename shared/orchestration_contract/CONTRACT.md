# Orchestration Contract

Every project pipeline must return:

- `project`
- `task`
- `confidence_threshold`
- `iterations`
- `confidence_score` (0..1)
- `confidence_label` (`low|medium|high`)
- `loop_terminated_reason` (`confidence_threshold_reached|max_iterations_reached|retry_with_additional_information`)
- `iteration_history` (list of per-iteration metrics)
- `decision_log` (list of routing decisions)
- `source` (public URL or fixture URI)
- `used_fallback` (boolean)
- `report_path` (path to generated markdown report)
- `summary_path` (path to generated summary json)
- `trace_path` (path to generated trace json)
