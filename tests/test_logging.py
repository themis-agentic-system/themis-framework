from __future__ import annotations

import io
import logging

import pytest

from api.logging_config import log_structured


@pytest.mark.parametrize(
    "message, kwargs, expected_substrings",
    [
        (
            "Received\n<script>alert(1)</script>",
            {"api_key": "super-secret", "note": "Line1\nLine2"},
            ["Received\\n", "***redacted***", "note=Line1\\nLine2"],
        ),
        (
            "Clean message",
            {"token": "abc123", "details": "normal"},
            ["Clean message", "***redacted***", "details=normal"],
        ),
    ],
)
def test_log_structured_sanitises_outputs(message: str, kwargs: dict[str, str], expected_substrings: list[str], caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("themis.tests.logging")
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    try:
        log_structured(logger, "INFO", message, **kwargs)
    finally:
        logger.removeHandler(handler)
        logger.propagate = True

    logged_message = stream.getvalue().strip()
    for fragment in expected_substrings:
        assert fragment in logged_message
    assert "<script" not in logged_message
    assert "\n" not in logged_message
