from __future__ import annotations

from copy import deepcopy

from packs.personal_injury.schema import load_matter
from packs.personal_injury.workflows import PHASES, active_phase, workflow_summary


def test_active_phase_defaults(sample_matter):
    plan = active_phase(sample_matter)
    assert plan.name == "litigation"
    assert plan.documents


def test_workflow_summary_includes_documents(sample_matter):
    summary = workflow_summary(sample_matter)
    assert "phase" in summary
    assert summary["documents"]
    assert any("Complaint" in title for title in summary["documents"])


def test_all_phases_registered():
    expected = {"intake", "pre_suit", "litigation", "adr", "trial"}
    assert expected.issubset(PHASES.keys())


def test_phase_branching(sample_payload):
    payload = deepcopy(sample_payload)
    payload["matter"]["metadata"]["phase"] = "adr"
    matter = load_matter(payload)
    plan = active_phase(matter)
    assert plan.name == "adr"
