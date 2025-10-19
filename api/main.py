"""FastAPI surface for the Themis orchestrator."""

from fastapi import FastAPI

from orchestrator.router import router as orchestrator_router

app = FastAPI(title="Themis Orchestrator API")


@app.on_event("startup")
async def startup() -> None:
    """Perform startup initialization hooks."""
    # Load orchestrator configuration, register agents, warm caches, etc.
    # Implementations should replace this stub with real startup logic.
    pass


app.include_router(orchestrator_router, prefix="/orchestrator", tags=["orchestrator"])


@app.get("/health", tags=["system"])
async def healthcheck() -> dict[str, str]:
    """Basic readiness probe for container orchestration."""
    return {"status": "ok"}
