from __future__ import annotations

import asyncio
import csv
from pathlib import Path

import pytest

from orchestrator.service import OrchestratorService
from orchestrator.storage.sqlite_repository import SQLiteOrchestratorStateRepository
from packs.pi_demand import run as pi_demand_run


FIXTURE_DIR = Path(__file__).resolve().parents[2] / "packs" / "pi_demand" / "fixtures"


@pytest.mark.parametrize(
    (
        "fixture_name",
        "expected_demand_phrases",
        "expected_complaint_phrases",
        "min_timeline_rows",
    ),
    [
        (
            "nominal_collision_matter.json",
            [
                "Subject: Settlement Demand",
                "Maria Lopez suffered shoulder and knee injuries",
                "Negotiation Positions:",
                "$210,000",
            ],
            [
                "COMPLAINT FOR DAMAGES",
                "Maria Lopez",
                "Motor Vehicle Negligence",
                "PRAYER FOR RELIEF",
            ],
            3,
        ),
        (
            "edgecase_sparse_slip_and_fall.json",
            [
                "Subject: Settlement Demand",
                "Maya Chen slipped on a puddle",
                "Dear Opposing Counsel",
                "Negotiation Positions:",
            ],
            [
                "COMPLAINT FOR DAMAGES",
                "Maya Chen",
                "Sunrise Market LLC",
                "Premises Liability",
            ],
            1,
        ),
    ],
)
def test_pi_demand_pack_generates_artifacts(
    tmp_path: Path,
    fixture_name: str,
    expected_demand_phrases: list[str],
    expected_complaint_phrases: list[str],
    min_timeline_rows: int,
) -> None:
    """Test that the PI demand pack generates all expected artifacts."""
    matter_path = FIXTURE_DIR / fixture_name
    matter = pi_demand_run.load_matter(matter_path)

    database_url = f"sqlite:///{tmp_path / 'state.db'}"
    repository = SQLiteOrchestratorStateRepository(database_url=database_url)
    service = OrchestratorService(repository=repository)

    execution = asyncio.run(service.execute(matter))

    assert execution["status"] == "complete"
    assert set(execution["artifacts"]) == {"lda", "dea", "lsa"}

    saved_paths = pi_demand_run.persist_outputs(matter, execution, output_root=tmp_path)

    matter_slug = matter["metadata"]["slug"]
    matter_output_dir = tmp_path / matter_slug

    # Check all expected files exist
    timeline_file = matter_output_dir / "timeline.csv"
    letter_file = matter_output_dir / "draft_demand_letter.txt"
    complaint_file = matter_output_dir / "draft_complaint.txt"
    checklist_file = matter_output_dir / "evidence_checklist.txt"
    medical_file = matter_output_dir / "medical_expense_summary.csv"
    statute_file = matter_output_dir / "statute_tracker.txt"

    assert timeline_file.exists(), "Timeline file should exist"
    assert letter_file.exists(), "Demand letter should exist"
    assert complaint_file.exists(), "Complaint should exist"
    assert checklist_file.exists(), "Evidence checklist should exist"
    assert medical_file.exists(), "Medical summary should exist"
    assert statute_file.exists(), "Statute tracker should exist"

    assert len(saved_paths) == 6, f"Should generate 6 artifacts, got {len(saved_paths)}"

    # Validate timeline CSV
    with timeline_file.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= min_timeline_rows
    assert all(row["description"].strip() for row in rows)

    # Validate demand letter
    letter_content = letter_file.read_text(encoding="utf-8")
    for phrase in expected_demand_phrases:
        assert phrase in letter_content, (
            f"Expected phrase '{phrase}' not in demand letter"
        )

    # Validate complaint
    complaint_content = complaint_file.read_text(encoding="utf-8")
    for phrase in expected_complaint_phrases:
        assert phrase in complaint_content, (
            f"Expected phrase '{phrase}' not in complaint"
        )

    # Validate checklist
    checklist_content = checklist_file.read_text(encoding="utf-8")
    assert "EVIDENCE CHECKLIST" in checklist_content
    assert "DOCUMENTS REQUIRED" in checklist_content

    # Validate medical summary has CSV header
    medical_content = medical_file.read_text(encoding="utf-8")
    assert "Date,Provider,Service,Amount,Status" in medical_content

    # Validate statute tracker
    statute_content = statute_file.read_text(encoding="utf-8")
    assert "STATUTE OF LIMITATIONS TRACKER" in statute_content
    jurisdiction = matter.get("metadata", {}).get("jurisdiction", "California")
    assert jurisdiction in statute_content

    # Running persist_outputs again should be idempotent and not raise
    second_saved_paths = pi_demand_run.persist_outputs(
        matter, execution, output_root=tmp_path
    )
    assert len(second_saved_paths) == 6


def test_jurisdiction_aware_complaint_generation(tmp_path: Path) -> None:
    """Test that complaints vary by jurisdiction."""
    database_url = f"sqlite:///{tmp_path / 'state.db'}"
    repository = SQLiteOrchestratorStateRepository(database_url=database_url)
    service = OrchestratorService(repository=repository)

    # Test California fixture
    ca_matter = pi_demand_run.load_matter(FIXTURE_DIR / "sample_matter.json")
    ca_execution = asyncio.run(service.execute(ca_matter))
    pi_demand_run.persist_outputs(ca_matter, ca_execution, output_root=tmp_path)

    ca_complaint = (
        tmp_path / ca_matter["metadata"]["slug"] / "draft_complaint.txt"
    ).read_text()

    # California-specific elements
    assert "California" in ca_complaint or "CA" in ca_complaint
    assert "COMPLAINT FOR DAMAGES" in ca_complaint
    assert (
        "Motor Vehicle" in ca_complaint
    )  # Check for California motor vehicle cause of action

    # Test statute tracker includes jurisdiction info
    ca_statute = (
        tmp_path / ca_matter["metadata"]["slug"] / "statute_tracker.txt"
    ).read_text()
    assert "California" in ca_statute
    assert "2 years" in ca_statute  # CA SOL for PI
