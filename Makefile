.PHONY: test run run-all report

PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PROJECT ?= 01-eval-driven-agent

test:
	$(PYTHON) -m pytest -q

run:
	$(PYTHON) run_project.py --project $(PROJECT)

run-all:
	$(PYTHON) run_project.py --project 01-eval-driven-agent
	$(PYTHON) run_project.py --project 02-multi-agent-debate-judge
	$(PYTHON) run_project.py --project 03-human-in-the-loop-review
	$(PYTHON) run_project.py --project 04-adaptive-rag-depth
	$(PYTHON) run_project.py --project 05-agent-observability-tracing
	$(PYTHON) run_project.py --project 06-guardrail-policy-engine
	$(PYTHON) run_project.py --project 07-self-improving-prompt-policy-tuner
	$(PYTHON) run_project.py --project 08-cost-quality-model-router

report: run-all
	@echo "Reports generated under reports/"
