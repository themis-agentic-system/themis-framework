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
    ("fixture_name", "expected_phrases", "min_timeline_rows"),
    [
        (
            "nominal_collision_matter.json",
            [
                "Subject: Settlement Demand",
                "Maria Lopez suffered shoulder and knee injuries",
                "Negotiation Positions:",
                "$210,000",
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
            1,
        ),
    ],
)
def test_pi_demand_pack_generates_artifacts(
    tmp_path: Path, fixture_name: str, expected_phrases: list[str], min_timeline_rows: int
) -> None:
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
    timeline_file = matter_output_dir / "timeline.csv"
    letter_file = matter_output_dir / "draft_demand_letter.txt"

    assert timeline_file.exists()
    assert letter_file.exists()
    assert set(saved_paths) == {timeline_file, letter_file}

    with timeline_file.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= min_timeline_rows
    assert all(row["description"].strip() for row in rows)

    letter_content = letter_file.read_text(encoding="utf-8")
    for phrase in expected_phrases:
        assert phrase in letter_content

    # Running persist_outputs again should be idempotent and not raise.
    second_saved_paths = pi_demand_run.persist_outputs(matter, execution, output_root=tmp_path)
    assert set(second_saved_paths) == {timeline_file, letter_file}
