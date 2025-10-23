"""Routing layer exposing orchestrator operations via FastAPI."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.security import verify_api_key
from orchestrator.service import OrchestratorService

router = APIRouter()
_service: OrchestratorService | None = None

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class PlanRequest(BaseModel):
    """Request payload for planning operations."""

    model_config = ConfigDict(extra="forbid")

    matter: dict[str, Any]


class ExecuteRequest(BaseModel):
    """Request payload for executing previously generated plans."""

    model_config = ConfigDict(extra="forbid")

    plan_id: str | None = None
    matter: dict[str, Any] | None = None


def configure_service(service: OrchestratorService) -> None:
    """Register the orchestrator service instance used by the router."""

    global _service
    _service = service


def get_service() -> OrchestratorService:
    """Return the configured orchestrator service, creating one if missing."""

    global _service
    if _service is None:
        _service = OrchestratorService()
    return _service


@router.post("/plan", summary="Create an execution plan for a legal matter")
@limiter.limit("20/minute")  # 20 requests per minute per IP
async def plan(
    request_body: PlanRequest,
    request: Request,
    api_key: str = Depends(verify_api_key),
) -> dict[str, Any]:
    """Generate a draft plan given a matter payload.

    Requires authentication via Bearer token if THEMIS_API_KEY is set.
    Rate limited to 20 requests per minute per IP address.
    """
    service = get_service()
    return await service.plan(request_body.matter)


@router.post("/execute", summary="Run a plan through registered agents")
@limiter.limit("10/minute")  # 10 requests per minute per IP (lower limit for expensive operations)
async def execute(
    request_body: ExecuteRequest,
    request: Request,
    api_key: str = Depends(verify_api_key),
) -> dict[str, Any]:
    """Run a matter through the orchestrated workflow.

    Requires authentication via Bearer token if THEMIS_API_KEY is set.
    Rate limited to 10 requests per minute per IP address.
    """
    if request_body.plan_id is None and request_body.matter is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either an existing plan_id or a matter payload to execute.",
        )

    service = get_service()
    try:
        return await service.execute(plan_id=request_body.plan_id, matter=request_body.matter)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/plans/{plan_id}", summary="Retrieve a previously generated plan")
@limiter.limit("60/minute")  # 60 requests per minute per IP (higher limit for read operations)
async def get_plan(
    plan_id: str,
    request: Request,
    api_key: str = Depends(verify_api_key),
) -> dict[str, Any]:
    """Fetch a plan definition by identifier.

    Requires authentication via Bearer token if THEMIS_API_KEY is set.
    Rate limited to 60 requests per minute per IP address.
    """
    service = get_service()
    try:
        return await service.get_plan(plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/artifacts/{plan_id}", summary="Retrieve execution artifacts for a plan")
@limiter.limit("60/minute")  # 60 requests per minute per IP (higher limit for read operations)
async def get_artifacts(
    plan_id: str,
    request: Request,
    api_key: str = Depends(verify_api_key),
) -> dict[str, Any]:
    """Fetch artifacts generated during execution for a plan.

    Requires authentication via Bearer token if THEMIS_API_KEY is set.
    Rate limited to 60 requests per minute per IP address.
    """
    service = get_service()
    try:
        return await service.get_artifacts(plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
