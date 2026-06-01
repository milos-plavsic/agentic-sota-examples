"""FastAPI for agentic-sota-examples.

Provides REST endpoints to invoke each agentic pattern.
Auth and rate-limiting use the shared ml-core package:
  - ml_core.APIKeyMiddleware  — X-API-Key header validation (env: API_KEY)
  - ml_core.RateLimiter       — token-bucket, 60 req/s burst 120 per IP
"""

from __future__ import annotations

import importlib
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# ml-core imports with graceful fallback
# ---------------------------------------------------------------------------
try:
    from ml_core import (
        APIKeyMiddleware,
        RateLimiter,
        RateLimitExceeded,
        configure_logging,
        install_middleware,
    )
    from ml_core.exceptions import ApplicationError

    _ML_CORE = True
except ImportError:
    _ML_CORE = False
    from ml_core import (
        configure_logging,  # type: ignore[assignment]
        install_middleware,  # type: ignore[assignment]
    )
    from ml_core.exceptions import ApplicationError  # type: ignore[assignment]

    class RateLimitExceeded(Exception):  # type: ignore[no-redef]
        pass

    RateLimiter = None  # type: ignore[assignment,misc]
    APIKeyMiddleware = None  # type: ignore[assignment]

logger = configure_logging("agentic-sota")

app = FastAPI(
    title="Agentic SOTA Examples",
    version="1.0.0",
    description="REST API for running agentic pattern pipelines",
)

install_middleware(app, cors_allow_origins=("*",), cors_allow_credentials=False)

if _ML_CORE and APIKeyMiddleware is not None:
    app.add_middleware(
        APIKeyMiddleware,
        public_paths=("/health", "/metrics", "/docs", "/openapi.json"),
    )

# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
if _ML_CORE and RateLimiter is not None:
    _limiter: Any = RateLimiter(rate=60.0, burst=120.0)
else:
    _limiter = None


def _rate_limit(request: Request) -> None:
    if _limiter is None:
        return
    client_ip = request.client.host if request.client else "unknown"
    try:
        _limiter.acquire(client_ip)
    except RateLimitExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Pipeline registry
# ---------------------------------------------------------------------------

_PIPELINES: dict[str, str] = {
    "eval-driven-agent": "project_pipelines.p01_eval_driven_agent",
    "multi-agent-debate": "project_pipelines.p02_debate_judge",
    "human-in-the-loop": "project_pipelines.p03_human_review",
    "adaptive-rag": "project_pipelines.p04_adaptive_rag",
    "observability": "project_pipelines.p05_observability",
    "guardrail-policy": "project_pipelines.p06_guardrail_policy",
    "self-improver": "project_pipelines.p07_self_improver",
    "cost-quality-router": "project_pipelines.p08_cost_quality_router",
}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class RunPipelineRequest(BaseModel):
    """Request body for running a pipeline."""

    topic: str = Field(..., min_length=1, max_length=300, description="Query topic")
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0)
    max_iterations: int = Field(3, ge=1, le=10)
    extra: dict[str, Any] = Field(default_factory=dict, description="Pipeline-specific config")


class HealthResponse(BaseModel):
    status: str
    version: str
    pipelines: list[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    """Health check."""
    return HealthResponse(
        status="ok",
        version=app.version,
        pipelines=sorted(_PIPELINES.keys()),
    )


@app.get("/v1/pipelines", tags=["pipelines"])
async def list_pipelines(_rl: None = Depends(_rate_limit)) -> dict:
    """List all available agentic pipelines."""
    return {
        "total": len(_PIPELINES),
        "pipelines": [{"id": pid, "module": mod} for pid, mod in sorted(_PIPELINES.items())],
    }


@app.post("/v1/run/{pipeline_id}", tags=["pipelines"])
async def run_pipeline(
    pipeline_id: str,
    body: RunPipelineRequest,
    _rl: None = Depends(_rate_limit),
) -> dict:
    """Run a named agentic pipeline and return its result.

    pipeline_id must be one of the registered pipeline IDs
    (see GET /v1/pipelines).
    """
    if pipeline_id not in _PIPELINES:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline '{pipeline_id}' not found. "
            f"Available: {sorted(_PIPELINES.keys())}",
        )

    module_path = _PIPELINES[pipeline_id]
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        logger.error("Failed to import pipeline %s: %s", pipeline_id, exc)
        raise HTTPException(status_code=500, detail=f"Pipeline module unavailable: {exc}") from exc

    cfg: dict[str, object] = {
        "project": pipeline_id,
        "task": "api_run",
        "topic": body.topic,
        "confidence_threshold": body.confidence_threshold,
        "max_iterations": body.max_iterations,
        **body.extra,
    }

    try:
        result: dict[str, object] = module.run(cfg)
    except Exception as exc:
        logger.error("Pipeline %s failed: %s", pipeline_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {exc}") from exc

    return result


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------


@app.exception_handler(ApplicationError)
async def app_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    logger.error("ApplicationError: %s", exc)
    return JSONResponse(status_code=getattr(exc, "status_code", 400), content={"detail": str(exc)})


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
