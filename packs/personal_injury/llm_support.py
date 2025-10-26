"""Helper utilities for jurisdiction-specific LLM lookups."""

from __future__ import annotations

import asyncio
from typing import Any

from tools.llm_client import get_llm_client


def run_structured_prompt(
    *,
    system_prompt: str,
    user_prompt: str,
    response_format: dict[str, Any],
) -> dict[str, Any]:
    """Execute a structured LLM prompt with graceful fallbacks.

    The helper hides asyncio plumbing so pack modules can remain synchronous.
    When the runtime LLM client operates in stub mode (the default for tests),
    this call is deterministic. If the environment cannot execute the prompt
    (for example when an event loop is already running), an empty payload is
    returned so callers can fall back to baseline heuristics.
    """

    client = get_llm_client()
    try:
        try:
            return asyncio.run(
                client.generate_structured(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_format=response_format,
                    max_tokens=1024,
                )
            )
        except RuntimeError:
            # asyncio.run cannot be nested inside an already running loop.
            # In that situation we gracefully return an empty payload so
            # downstream logic can use deterministic defaults instead of
            # raising an exception that would interrupt document rendering.
            return {}
    except Exception:
        # Network errors or SDK failures should not prevent document
        # generation. Callers will merge the empty payload with defaults.
        return {}
