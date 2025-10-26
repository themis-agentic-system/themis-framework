"""FastAPI surface for the Themis orchestrator."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api.logging_config import configure_logging
from api.middleware import (
    AuditLoggingMiddleware,
    CostTrackingMiddleware,
    PayloadSizeLimitMiddleware,
    RequestLoggingMiddleware,
)
from orchestrator.router import configure_service
from orchestrator.router import router as orchestrator_router
from orchestrator.service import OrchestratorService
from tools.metrics import metrics_registry

# Configure logging first
configure_logging()

logger = logging.getLogger("themis.api")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown).

    This replaces the deprecated @app.on_event decorators with
    a modern context manager approach.
    """
    # Startup: Initialize the orchestrator service
    logger.info("Starting Themis Orchestrator API")
    service = OrchestratorService()
    configure_service(service)
    app.state.orchestrator_service = service
    logger.info("Orchestrator service initialized successfully")

    yield

    # Shutdown: Clean up resources (if needed in the future)
    logger.info("Shutting down Themis Orchestrator API")


app = FastAPI(
    title="Themis Orchestration API",
    description="Multi-agent legal analysis workflow orchestration.",
    version="0.1.0",
    lifespan=lifespan,
)

# Attach rate limiter to app state and add exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add middleware (order matters - last added is executed first)
app.add_middleware(AuditLoggingMiddleware)
app.add_middleware(CostTrackingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(PayloadSizeLimitMiddleware)  # Check payload size first

app.include_router(orchestrator_router, prefix="/orchestrator", tags=["orchestrator"])


@app.get("/", response_class=HTMLResponse, tags=["system"])
async def root() -> HTMLResponse:
    """Serve the landing page with document upload form."""
    static_dir = Path(__file__).parent / "static"
    index_path = static_dir / "index.html"

    if index_path.exists():
        return HTMLResponse(content=index_path.read_text())
    else:
        return HTMLResponse(
            content="""
            <html>
                <body>
                    <h1>Themis Orchestration API</h1>
                    <p>Multi-agent legal analysis workflow orchestration.</p>
                    <p><a href="/docs">API Documentation</a></p>
                </body>
            </html>
            """
        )


@app.get("/health", tags=["system"])
async def healthcheck() -> dict[str, str]:
    """Basic readiness probe for container orchestration."""
    return {"status": "ok"}


@app.get("/metrics", tags=["system"], response_class=PlainTextResponse)
async def metrics() -> PlainTextResponse:
    """Expose collected metrics in Prometheus text format."""

    return PlainTextResponse(content=metrics_registry.render(), media_type="text/plain; version=0.0.4")
