from project_pipelines.p01_eval_driven_agent import run as run_p01
from project_pipelines.p02_debate_judge import run as run_p02
from project_pipelines.p03_human_review import run as run_p03
from project_pipelines.p04_adaptive_rag import run as run_p04
from project_pipelines.p05_observability import run as run_p05
from project_pipelines.p06_guardrail_policy import run as run_p06
from project_pipelines.p07_self_improver import run as run_p07
from project_pipelines.p08_cost_quality_router import run as run_p08

PROJECT_RUNNERS = {
    "01-eval-driven-agent": run_p01,
    "02-multi-agent-debate-judge": run_p02,
    "03-human-in-the-loop-review": run_p03,
    "04-adaptive-rag-depth": run_p04,
    "05-agent-observability-tracing": run_p05,
    "06-guardrail-policy-engine": run_p06,
    "07-self-improving-prompt-policy-tuner": run_p07,
    "08-cost-quality-model-router": run_p08,
}
