# Release Notes 2026-04

## Stabilization Pass

- Completed all six implementation phases from the SOTA monorepo plan.
- Added full mixed CI model with strict PR smoke gates and nightly expanded runs.
- Added acceptance criteria coverage with end-to-end artifact checks.
- Added fallback behavior test to ensure CI resilience under internet source failures.
- Added shared testing constants under `shared/testing/`.

## Structure Harmonization

- Set canonical contract location to `shared/orchestration_contract/CONTRACT.md`.
- Set canonical policy package to `shared/orchestration_policy/policy.py`.
- Kept compatibility files (`shared/orchestration_policy.py`, `shared/orchestration_contract.md`) as pointers/re-exports.

## Outputs

- All 8 projects runnable through `make run` / `make report`.
- Standardized outputs per run:
  - `summary.json`
  - `REPORT.md`
  - trace artifact JSON
