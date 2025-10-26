from __future__ import annotations

from packs.personal_injury.config import DOCUMENTS, build_generator
from packs.personal_injury.schema import matter_summary


def test_generators_render(sample_matter):
    for key in DOCUMENTS:
        generator = build_generator(key, sample_matter)
        output = generator.render()
        assert sample_matter.metadata.title in output
        assert "ANALYTICS CONTEXT" in output
        summary = matter_summary(sample_matter)
        assert str(summary["matter_id"]) in output


def test_discovery_generator_sections(sample_matter):
    discovery = build_generator("discovery", sample_matter).render()
    assert "Interrogatory" in discovery
    assert "Request for Production" in discovery
    assert "Request for Admission" in discovery
