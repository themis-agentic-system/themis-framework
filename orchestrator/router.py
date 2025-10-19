"""Routing layer exposing orchestrator operations via FastAPI."""

from fastapi import APIRouter

from orchestrator.service import OrchestratorService

router = APIRouter()
service = OrchestratorService()


@router.post("/plan", summary="Create an execution plan for a legal matter")
async def plan(matter: dict) -> dict:
    """Generate a draft plan given a matter payload."""
    return await service.plan(matter)


@router.post("/execute", summary="Run a plan through registered agents")
async def execute(matter: dict) -> dict:
    """Run a matter through the orchestrated workflow."""
    return await service.execute(matter)
