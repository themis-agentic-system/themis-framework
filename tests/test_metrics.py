"""Tests for the metrics registry and FastAPI exposition endpoint."""

from __future__ import annotations

import asyncio

from agents.lda import LDAAgent
from api.main import metrics as metrics_endpoint
from tools.metrics import metrics_registry


def test_agent_run_metrics_recorded(sample_matter: dict[str, object]) -> None:
    """Ensure agent runs produce duration and tool invocation metrics."""

    metrics_registry.reset()

    asyncio.run(LDAAgent().run(sample_matter))

    duration_histogram = metrics_registry.get_histogram("themis_agent_run_seconds")
    assert duration_histogram is not None

    samples = list(duration_histogram.samples())
    assert samples, "Expected histogram samples for LDA agent run"
    labels, _, _, count = samples[0]
    assert labels.get("agent") == "lda"
    assert count == 1

    tool_counter = metrics_registry.get_counter("themis_agent_tool_invocations_total")
    assert tool_counter is not None

    tool_samples = list(tool_counter.samples())
    lda_sample = next(
        (value for sample_labels, value in tool_samples if sample_labels.get("agent") == "lda"),
        None,
    )
    assert lda_sample is not None
    assert lda_sample >= 2


def test_metrics_endpoint_prometheus_output(sample_matter: dict[str, object]) -> None:
    """The /metrics endpoint should return scrape-compatible text."""

    metrics_registry.reset()
    asyncio.run(LDAAgent().run(sample_matter))

    response = asyncio.run(metrics_endpoint())

    assert response.status_code == 200
    body = response.body.decode()
    assert "themis_agent_run_seconds_bucket" in body
    assert 'agent="lda"' in body
    assert body.endswith("\n")
