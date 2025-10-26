"""In-memory metrics registry with Prometheus exposition support."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any


def _escape_label_value(value: Any) -> str:
    text = str(value)
    return text.replace("\\", r"\\").replace("\n", r"\n").replace('"', r"\"")


def _format_labels(labels: dict[str, Any]) -> str:
    if not labels:
        return ""
    parts = [f'{key}="{_escape_label_value(value)}"' for key, value in sorted(labels.items())]
    return "{" + ",".join(parts) + "}"


class CounterMetric:
    """Simple monotonically increasing counter."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self._values: dict[tuple[tuple[str, Any], ...], float] = defaultdict(float)

    def inc(self, value: float = 1.0, **labels: Any) -> None:
        """Increment the counter for the provided label set."""

        key = tuple(sorted(labels.items()))
        self._values[key] += value

    def samples(self) -> Iterator[tuple[dict[str, Any], float]]:
        for key, value in self._values.items():
            yield dict(key), value

    def render(self) -> list[str]:
        lines = [f"# HELP {self.name} {self.description}", f"# TYPE {self.name} counter"]
        for labels, value in sorted(
            self.samples(), key=lambda item: tuple(sorted(item[0].items()))
        ):
            lines.append(f"{self.name}{_format_labels(labels)} {value}")
        if len(lines) == 2:
            # Counters should still emit a zero sample to ensure discoverability.
            lines.append(f"{self.name} 0")
        return lines

    def reset(self) -> None:
        self._values.clear()


@dataclass
class _HistogramSample:
    bucket_counts: list[int]
    value_sum: float = 0.0
    value_count: int = 0


class HistogramMetric:
    """Fixed-bucket histogram compatible with Prometheus exposition."""

    def __init__(self, name: str, description: str, buckets: Iterable[float]) -> None:
        bucket_list = sorted(float(bucket) for bucket in buckets)
        if not bucket_list:
            raise ValueError("Histogram requires at least one bucket boundary")
        if bucket_list[-1] != float("inf"):
            bucket_list.append(float("inf"))
        self.name = name
        self.description = description
        self._buckets = bucket_list
        self._values: dict[tuple[tuple[str, Any], ...], _HistogramSample] = {}

    def observe(self, value: float, **labels: Any) -> None:
        """Record an observation for the provided label set."""

        key = tuple(sorted(labels.items()))
        sample = self._values.setdefault(
            key, _HistogramSample(bucket_counts=[0 for _ in self._buckets])
        )
        for index, upper in enumerate(self._buckets):
            if value <= upper:
                sample.bucket_counts[index] += 1
        sample.value_sum += value
        sample.value_count += 1

    def samples(
        self,
    ) -> Iterator[tuple[dict[str, Any], list[int], float, int]]:
        for key, sample in self._values.items():
            yield dict(key), sample.bucket_counts, sample.value_sum, sample.value_count

    def render(self) -> list[str]:
        lines = [f"# HELP {self.name} {self.description}", f"# TYPE {self.name} histogram"]
        for labels, bucket_counts, value_sum, value_count in sorted(
            self.samples(), key=lambda item: tuple(sorted(item[0].items()))
        ):
            cumulative = 0
            for upper, bucket_value in zip(self._buckets, bucket_counts):
                cumulative = bucket_value
                upper_label = "+Inf" if upper == float("inf") else str(upper)
                bucket_labels = labels | {"le": upper_label}
                lines.append(
                    f"{self.name}_bucket{_format_labels(bucket_labels)} {cumulative}"
                )
            lines.append(f"{self.name}_count{_format_labels(labels)} {value_count}")
            lines.append(f"{self.name}_sum{_format_labels(labels)} {value_sum}")
        if len(lines) == 2:
            # Emit empty histogram to satisfy Prometheus scrapes.
            for upper in self._buckets:
                upper_label = "+Inf" if upper == float("inf") else str(upper)
                bucket_labels = {"le": upper_label}
                lines.append(f"{self.name}_bucket{_format_labels(bucket_labels)} 0")
            lines.append(f"{self.name}_count 0")
            lines.append(f"{self.name}_sum 0")
        return lines

    def reset(self) -> None:
        self._values.clear()


class MetricsRegistry:
    """Container for counters and histograms exposed via the API."""

    def __init__(self) -> None:
        self._counters: dict[str, CounterMetric] = {}
        self._histograms: dict[str, HistogramMetric] = {}

    def counter(self, name: str, description: str) -> CounterMetric:
        if name not in self._counters:
            self._counters[name] = CounterMetric(name, description)
        return self._counters[name]

    def histogram(
        self, name: str, description: str, *, buckets: Iterable[float]
    ) -> HistogramMetric:
        if name not in self._histograms:
            self._histograms[name] = HistogramMetric(name, description, buckets)
        return self._histograms[name]

    def get_counter(self, name: str) -> CounterMetric | None:
        return self._counters.get(name)

    def get_histogram(self, name: str) -> HistogramMetric | None:
        return self._histograms.get(name)

    def render(self) -> str:
        lines: list[str] = []
        for metric in self._counters.values():
            lines.extend(metric.render())
        for metric in self._histograms.values():
            lines.extend(metric.render())
        return "\n".join(lines) + "\n"

    def reset(self) -> None:
        for metric in self._counters.values():
            metric.reset()
        for metric in self._histograms.values():
            metric.reset()


metrics_registry = MetricsRegistry()

__all__ = [
    "CounterMetric",
    "HistogramMetric",
    "MetricsRegistry",
    "metrics_registry",
]

