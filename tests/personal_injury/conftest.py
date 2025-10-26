from __future__ import annotations

import json
from pathlib import Path

import pytest

from packs.personal_injury.schema import PersonalInjuryMatter, load_matter


@pytest.fixture(scope="session")
def sample_matter() -> PersonalInjuryMatter:
    fixture_path = Path(__file__).parents[2] / "packs" / "personal_injury" / "fixtures" / "sample_matter.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    return load_matter(data)


@pytest.fixture(scope="session")
def sample_payload() -> dict[str, object]:
    fixture_path = Path(__file__).parents[2] / "packs" / "personal_injury" / "fixtures" / "sample_matter.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))
