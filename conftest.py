"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Generator

import pytest

from tools.metrics import metrics_registry


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register configuration options consumed by pytest-asyncio."""

    parser.addini("asyncio_mode", "Configure asyncio support", default="auto")


try:  # pragma: no cover - exercised indirectly during test discovery
    import pytest_asyncio  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - used in constrained environments
    @pytest.hookimpl(tryfirst=True)
    def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
        """Execute async tests using asyncio when pytest-asyncio is unavailable."""

        test_function = pyfuncitem.obj
        if inspect.iscoroutinefunction(test_function):
            loop = asyncio.new_event_loop()
            try:
                signature = inspect.signature(test_function)
                kwargs = {
                    name: pyfuncitem.funcargs[name]
                    for name in signature.parameters
                    if name in pyfuncitem.funcargs
                }
                loop.run_until_complete(test_function(**kwargs))
            finally:
                loop.close()
            return True
        return None


@pytest.fixture(autouse=True)
def reset_metrics_registry() -> Generator[None, None, None]:
    """Ensure each test starts with a clean metrics registry."""

    metrics_registry.reset()
    yield
    metrics_registry.reset()


@pytest.fixture(autouse=True)
def clear_api_key_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent API key configuration from leaking between tests."""

    for variable in ("THEMIS_API_KEY", "THEMIS_API_KEY_PREVIOUS", "THEMIS_API_KEYS"):
        monkeypatch.delenv(variable, raising=False)


@pytest.fixture(autouse=True)
def restore_rate_limit_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset SlowAPI's request state between tests to avoid cross-test leakage."""

    # SlowAPI stores a thread-local state that can retain previous request contexts.
    # Clearing the state ensures isolated behaviour in API tests.
    try:
        from slowapi import context
    except Exception:  # pragma: no cover - best effort cleanup
        return

    context._thread_local = context.ThreadLocalState()
    monkeypatch.setattr(context, "_thread_local", context.ThreadLocalState())
