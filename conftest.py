"""Test configuration hooking async tests into asyncio.run."""

from __future__ import annotations

import asyncio
import inspect

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    """Automatically execute ``async def`` tests via ``asyncio.run``.

    The repository intentionally avoids hard dependencies on pytest-asyncio.
    This hook mirrors the behaviour of ``asyncio_mode = auto`` so that
    coroutine tests run without additional plugins.
    """

    test_function = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_function):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(test_function(**pyfuncitem.funcargs))
        finally:
            loop.close()
        return True
    return None
