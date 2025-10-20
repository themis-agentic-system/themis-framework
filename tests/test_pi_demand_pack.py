from __future__ import annotations

from pathlib import Path

import pytest

from packs.pi_demand.run import load_matter, persist_outputs


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "packs" / "pi_demand" / "fixtures"
JSON_FIXTURE = FIXTURE_DIR / "sample_matter.json"
YAML_FIXTURE = FIXTURE_DIR / "sample_matter.yaml"


def test_load_matter_normalises_sample_fixture() -> None:
    matter = load_matter(JSON_FIXTURE)

    assert matter["summary"].startswith("Jane Smith suffered")
    assert matter["parties"] == ["Jane Smith (Client)", "Central Logistics, Inc."]
    assert matter["documents"], "Expected parsed documents"
    assert matter["metadata"]["slug"] == "smith-v-central-logistics"
    assert matter["matter_id"] == matter["metadata"]["id"]
    assert any(issue["issue"].startswith("Negligence") for issue in matter["issues"])


def test_load_matter_requires_parties(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{\"summary\": \"Missing parties\"}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Matter must list at least one party"):
        load_matter(invalid_path)


def test_persist_outputs_creates_timeline_and_letter(tmp_path: Path) -> None:
    matter = load_matter(JSON_FIXTURE)

    execution_result = {
        "artifacts": {
            "lda": {
                "facts": {
                    "fact_pattern_summary": [
                        "Collision occurred on 2024-03-14 at Mission & 5th.",
                    ],
                    "timeline": [
                        {"date": "2024-03-14", "description": "Collision"},
                        {"date": "2024-03-20", "description": "Initial treatment"},
                    ],
                }
            },
            "dea": {
                "legal_analysis": {
                    "issues": [
                        {"issue": "Negligence under Cal. Civ. Code § 1714"},
                    ],
                }
            },
            "lsa": {
                "strategy": {
                    "negotiation_positions": {
                        "opening": "$150,000",
                        "fallback": "$115,000",
                    },
                    "recommended_actions": ["Deliver demand letter to opposing counsel"],
                    "contingencies": ["File complaint if no response within 21 days"],
                    "risk_assessment": {
                        "confidence": 72,
                        "unknowns": ["Updated radiology report pending"],
                    },
                }
            },
        }
    }

    saved = persist_outputs(matter, execution_result, output_root=tmp_path)

    assert saved, "Expected at least one persisted artifact"

    matter_slug = matter["metadata"]["slug"]
    timeline_file = tmp_path / matter_slug / "timeline.csv"
    letter_file = tmp_path / matter_slug / "draft_demand_letter.txt"

    assert timeline_file.exists()
    assert letter_file.exists()

    timeline_lines = timeline_file.read_text(encoding="utf-8").splitlines()
    assert timeline_lines[0] == "date,description"
    assert any("Collision" in line for line in timeline_lines[1:])

    letter_content = letter_file.read_text(encoding="utf-8")
    assert "Settlement Demand" in letter_content
    assert matter["metadata"]["title"] in letter_content
    assert "$150,000" in letter_content

    # Persisted paths should include both artifacts.
    assert {timeline_file, letter_file}.issubset(set(saved))


def test_load_matter_supports_yaml_when_dependency_available() -> None:
    pytest.importorskip("yaml")

    matter = load_matter(YAML_FIXTURE)

    assert matter["metadata"]["slug"] == "smith-v-central-logistics"
