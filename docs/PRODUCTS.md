# Product catalog

| Service | Repository | Default local URL |
|---------|------------|-------------------|
| Agent pattern library | this repo | `make run PROJECT=01-eval-driven-agent` |
| AutoML Studio | [agentic-ml-pipeline](https://github.com/milos-plavsic/agentic-ml-pipeline) | `http://127.0.0.1:8000/ui` |
| Tabular benchmark | [tabular-ensemble-arena](https://github.com/milos-plavsic/tabular-ensemble-arena) | `:8000/docs` |
| Research analyst | [langgraph-research-analyst](https://github.com/milos-plavsic/langgraph-research-analyst) | `:8000/docs` |
| Knowledge tutor | [knowledge-graph-tutor](https://github.com/milos-plavsic/knowledge-graph-tutor) | `:8000/ui` |
| Market intel | [market-intel-multi-agent-terminal](https://github.com/milos-plavsic/market-intel-multi-agent-terminal) | `:8000/ui` |
| Incident copilot | [ai-incident-response-copilot](https://github.com/milos-plavsic/ai-incident-response-copilot) | `:8000/ui` |
| Refactor agent | [autonomous-refactor-agent](https://github.com/milos-plavsic/autonomous-refactor-agent) | `:8000/ui` |
| Enterprise RAG | [enterprise-rag-system](https://github.com/milos-plavsic/enterprise-rag-system) | `:8000/ui` |
| Learning paths | [personalized-learning-path-agent](https://github.com/milos-plavsic/personalized-learning-path-agent) | `:8000/ui` |

Shared libraries: [ml-core](https://github.com/milos-plavsic/ml-core), [agent-core](https://github.com/milos-plavsic/agent-core).

## Product console

```bash
cd console && npm install && npm run dev
```

Opens the Next.js console on port **3100** with live `/health` probes for each service.

Suggested local port map (override via your process manager):

| Port | Service |
|------|---------|
| 8000 | AutoML Studio |
| 8001 | Research Analyst |
| 8002 | Knowledge Tutor |
| 8003 | Market Intel |
| 8004 | Incident Copilot |
| 8005 | Refactor Agent |
| 8006 | Enterprise RAG |
| 8007 | Learning Paths |
| 8008 | Tabular Arena |
| 8009 | Categorical Boost |
| 8010 | NN Predictor |
| 5000 | MLflow tracking UI (`docker compose -f docker-compose.mlflow.yml up` in agentic-ml-pipeline) |
