from __future__ import annotations

from pathlib import Path

import pytest

from packs.criminal_defense.run import load_matter, persist_outputs

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "packs" / "criminal_defense" / "fixtures"
DUI_FIXTURE = FIXTURE_DIR / "dui_california.json"
DRUG_FIXTURE = FIXTURE_DIR / "drug_possession_warrant_new_york.json"


def test_load_matter_normalises_dui_fixture() -> None:
    matter = load_matter(DUI_FIXTURE)

    assert matter["client"]["name"] == "Maria Rodriguez"
    assert matter["metadata"]["jurisdiction"] == "California"
    assert len(matter["charges"]) == 2
    assert matter["metadata"]["case_number"] == "24CR12345"
    assert "constitutional_issues" in matter
    assert len(matter["constitutional_issues"]) > 0


def test_load_matter_requires_client() -> None:
    import json
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"matter": {"charges": [{"statute": "PC 123", "description": "Test"}], "arrest": {"date": "2024-01-01"}}}, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="client"):
            load_matter(temp_path)
    finally:
        temp_path.unlink()


def test_load_matter_requires_charges() -> None:
    import json
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"matter": {"client": {"name": "Test"}, "arrest": {"date": "2024-01-01"}}}, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="charges"):
            load_matter(temp_path)
    finally:
        temp_path.unlink()


def test_load_matter_requires_arrest() -> None:
    import json
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"matter": {"client": {"name": "Test"}, "charges": [{"statute": "PC 123", "description": "Test"}]}}, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="arrest"):
            load_matter(temp_path)
    finally:
        temp_path.unlink()


def test_persist_outputs_creates_artifacts(tmp_path: Path) -> None:
    matter = load_matter(DUI_FIXTURE)

    execution_result = {
        "artifacts": {
            "cca": {
                "constitutional_analysis": {
                    "fourth_amendment_issues": [
                        {"type": "warrantless_search", "severity": "high"},
                    ],
                }
            },
            "dms": {
                "discovery_demand": "Full discovery demand text here"
            },
            "lsw": {
                "suppression_motion": "Motion to suppress text here"
            },
        }
    }

    saved = persist_outputs(matter, execution_result, output_root=tmp_path)

    assert saved, "Expected at least one persisted artifact"

    case_slug = matter["metadata"]["slug"]
    timeline_file = tmp_path / case_slug / "case_timeline.csv"
    discovery_file = tmp_path / case_slug / "discovery_demand.txt"
    analysis_file = tmp_path / case_slug / "constitutional_issues_analysis.txt"

    assert timeline_file.exists(), f"Timeline file should exist at {timeline_file}"
    assert discovery_file.exists(), f"Discovery file should exist at {discovery_file}"
    assert analysis_file.exists(), f"Analysis file should exist at {analysis_file}"

    # Check timeline content
    timeline_content = timeline_file.read_text(encoding="utf-8")
    assert "date,event,constitutional_flag" in timeline_content

    # Check discovery content
    discovery_content = discovery_file.read_text(encoding="utf-8")
    assert "24CR12345" in discovery_content
    assert "California" in discovery_content or "discovery" in discovery_content.lower()

    # Check that artifacts are in saved paths
    assert timeline_file in saved
    assert discovery_file in saved


def test_load_matter_drug_possession_fixture() -> None:
    matter = load_matter(DRUG_FIXTURE)

    assert matter["client"]["name"] == "James Thompson"
    assert matter["metadata"]["jurisdiction"] == "New York"
    assert matter["metadata"]["case_type"] == "felony"
    assert "search_and_seizure" in matter
    assert matter["search_and_seizure"]["search_type"] == "warrant"
    assert len(matter["constitutional_issues"]) > 0


def test_persist_outputs_generates_suppression_motion_when_warranted(tmp_path: Path) -> None:
    matter = load_matter(DUI_FIXTURE)

    # Ensure constitutional issues are present
    assert "constitutional_issues" in matter
    assert len(matter["constitutional_issues"]) > 0

    execution_result = {
        "artifacts": {
            "cca": {
                "constitutional_analysis": "Fourth Amendment violation identified"
            },
            "dms": {
                "discovery_demand": "Discovery demand text"
            },
            "lsw": {
                "suppression_motion": "MOTION TO SUPPRESS - Fourth Amendment violation"
            },
        }
    }

    saved = persist_outputs(matter, execution_result, output_root=tmp_path)

    case_slug = matter["metadata"]["slug"]
    motion_file = tmp_path / case_slug / "motion_to_suppress.txt"

    # Motion should be generated because constitutional issues are present
    assert motion_file.exists(), "Motion to suppress should be generated when constitutional issues present"

    motion_content = motion_file.read_text(encoding="utf-8")
    assert "MOTION TO SUPPRESS" in motion_content
    assert motion_file in saved


def test_all_fixtures_load_successfully() -> None:
    """Test that all fixture files load without errors."""
    fixtures = [
        "dui_california.json",
        "drug_possession_warrant_new_york.json",
        "theft_burglary_texas.json",
        "fraud_florida.json",
        "assault_domestic_violence_illinois.json",
    ]

    for fixture_name in fixtures:
        fixture_path = FIXTURE_DIR / fixture_name
        assert fixture_path.exists(), f"Fixture {fixture_name} should exist"

        matter = load_matter(fixture_path)
        assert matter is not None
        assert "client" in matter
        assert "charges" in matter
        assert "arrest" in matter
        assert "metadata" in matter
