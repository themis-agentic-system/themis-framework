from __future__ import annotations

import json
from pathlib import Path

import pytest

from packs.personal_injury.schema import PersonalInjuryMatter, load_matter

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "packs" / "personal_injury" / "fixtures"
JSON_FIXTURE = FIXTURE_DIR / "sample_matter.json"


def test_load_matter_maps_schema() -> None:
    payload = json.loads(JSON_FIXTURE.read_text(encoding="utf-8"))
    matter = load_matter(payload)
    assert isinstance(matter, PersonalInjuryMatter)
    assert matter.metadata.title == "Smith v. Central Logistics"
    assert matter.parties[0].role == "plaintiff"
    assert matter.damages.total() > 0
    assert matter.insurance


def test_load_matter_requires_summary(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        load_matter(json.loads(invalid_path.read_text(encoding="utf-8")))


def test_matter_contains_medical_records() -> None:
    matter = load_matter(json.loads(JSON_FIXTURE.read_text(encoding="utf-8")))
    assert matter.medical_providers
    assert any(provider.records for provider in matter.medical_providers)
