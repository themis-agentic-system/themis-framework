"""Routing layer exposing orchestrator operations via FastAPI."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict

from orchestrator.service import OrchestratorService

router = APIRouter()
_service: OrchestratorService | None = None


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
async def plan(request: PlanRequest) -> dict[str, Any]:
    """Generate a draft plan given a matter payload."""

    service = get_service()
    return await service.plan(request.matter)


@router.post("/execute", summary="Run a plan through registered agents")
async def execute(request: ExecuteRequest) -> dict[str, Any]:
    """Run a matter through the orchestrated workflow."""

    if request.plan_id is None and request.matter is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either an existing plan_id or a matter payload to execute.",
        )

    service = get_service()
    try:
        return await service.execute(plan_id=request.plan_id, matter=request.matter)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/plans/{plan_id}", summary="Retrieve a previously generated plan")
async def get_plan(plan_id: str) -> dict[str, Any]:
    """Fetch a plan definition by identifier."""

    service = get_service()
    try:
        return await service.get_plan(plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/artifacts/{plan_id}", summary="Retrieve execution artifacts for a plan")
async def get_artifacts(plan_id: str) -> dict[str, Any]:
    """Fetch artifacts generated during execution for a plan."""

    service = get_service()
    try:
        return await service.get_artifacts(plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
