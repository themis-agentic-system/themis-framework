"""FastAPI surface for the Themis orchestrator."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from orchestrator.router import configure_service, router as orchestrator_router
from orchestrator.service import OrchestratorService
from tools.metrics import metrics_registry

app = FastAPI(title="Themis Orchestrator API")


@app.on_event("startup")
async def startup() -> None:
    """Perform startup initialization hooks."""
    service = OrchestratorService()
    configure_service(service)
    app.state.orchestrator_service = service


app.include_router(orchestrator_router, prefix="/orchestrator", tags=["orchestrator"])


@app.get("/health", tags=["system"])
async def healthcheck() -> dict[str, str]:
    """Basic readiness probe for container orchestration."""
    return {"status": "ok"}


@app.get("/metrics", tags=["system"], response_class=PlainTextResponse)
async def metrics() -> PlainTextResponse:
    """Expose collected metrics in Prometheus text format."""

    return PlainTextResponse(content=metrics_registry.render(), media_type="text/plain; version=0.0.4")
