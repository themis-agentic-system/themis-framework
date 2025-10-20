"""Smoke checks for higher-level system wiring used as QA gates."""

from importlib import import_module

import pytest

MODULES = (
    "api.main",
    "orchestrator.service",
    "packs.pi_demand.run",
)


@pytest.mark.parametrize("module_path", MODULES)
def test_module_importable(module_path: str) -> None:
    """Ensure critical modules remain importable."""
    import_module(module_path)
