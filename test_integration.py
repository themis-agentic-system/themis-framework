"""Integration test to verify full orchestration flow."""

import asyncio
from orchestrator.service import OrchestratorService
from orchestrator.storage.sqlite_repository import SQLiteOrchestratorStateRepository


async def test_full_orchestration():
    """Test complete orchestration with signal propagation."""

    # Create a temporary database
    database_url = "sqlite:////tmp/integration_test.db"
    repository = SQLiteOrchestratorStateRepository(database_url=database_url)
    service = OrchestratorService(repository=repository)

    # Create a matter
    matter = {
        "summary": "Integration test case - Alice was injured when Bob's vehicle struck her",
        "parties": ["Alice (Client)", "Bob (Defendant)"],
        "documents": [
            {
                "title": "Police Report",
                "date": "2024-01-15",
                "summary": "Bob failed to yield at intersection",
                "facts": [
                    "Bob ran red light",
                    "Alice had green light",
                ],
            }
        ],
        "events": [
            {"date": "2024-01-15", "description": "Collision occurred"},
            {"date": "2024-01-20", "description": "Alice sought medical treatment"},
        ],
        "issues": [
            {
                "issue": "Negligence - failure to yield",
                "facts": ["Bob ran red light"],
            }
        ],
        "authorities": [
            {"cite": "Vehicle Code § 123", "summary": "Duty to obey traffic signals"},
        ],
        "goals": {
            "settlement": "$50,000",
            "fallback": "$30,000",
        },
        "strengths": ["Clear liability", "Witness testimony"],
        "weaknesses": ["Limited documentation"],
        "concessions": ["Willing to accept structured settlement"],
        "evidentiary_gaps": ["Need medical records"],
        "confidence_score": 75,
    }

    # Execute the full workflow
    print("\n=== Running Full Orchestration ===\n")
    execution = await service.execute(matter)

    # Verify execution status
    print(f"Execution Status: {execution['status']}")
    assert execution["status"] == "complete", f"Expected 'complete', got '{execution['status']}'"

    # Check all phases completed
    phases_completed = []
    for step in execution.get("steps", []):
        phase = step.get("phase")
        status = step.get("status")
        print(f"  Phase: {phase:25s} Status: {status}")
        phases_completed.append(phase)

        # Verify no missing signals
        if status == "attention_required":
            missing = step.get("missing_signals", [])
            print(f"    WARNING: Missing signals: {missing}")
            assert False, f"Phase {phase} has missing signals: {missing}"

    # Verify all expected phases ran
    expected_phases = [
        "intake_facts",
        "issue_framing",
        "research_retrieval",
        "application_analysis",
        "draft_review",
    ]
    assert phases_completed == expected_phases, f"Phase mismatch: {phases_completed}"

    # Verify all agents produced artifacts
    artifacts = execution.get("artifacts", {})
    print(f"\nArtifacts produced: {list(artifacts.keys())}")
    assert "lda" in artifacts, "Missing LDA artifacts"
    assert "dea" in artifacts, "Missing DEA artifacts"
    assert "lsa" in artifacts, "Missing LSA artifacts"

    # Verify LDA produced facts
    lda_output = artifacts["lda"]
    assert "facts" in lda_output, "LDA should produce facts"
    facts = lda_output["facts"]
    assert "fact_pattern_summary" in facts, "Facts should have fact_pattern_summary"
    assert "timeline" in facts, "Facts should have timeline"
    print(f"  LDA: {len(facts.get('fact_pattern_summary', []))} facts, {len(facts.get('timeline', []))} timeline entries")

    # Verify DEA produced legal analysis and authorities
    dea_output = artifacts["dea"]
    assert "legal_analysis" in dea_output, "DEA should produce legal_analysis"
    assert "authorities" in dea_output, "DEA should produce authorities signal"

    authorities = dea_output["authorities"]
    assert isinstance(authorities, dict), "Authorities should be a dict"
    assert "controlling_authorities" in authorities, "Should have controlling_authorities"
    assert "contrary_authorities" in authorities, "Should have contrary_authorities"
    print(f"  DEA: {len(authorities.get('controlling_authorities', []))} controlling, {len(authorities.get('contrary_authorities', []))} contrary")

    # Verify LSA produced strategy and draft
    lsa_output = artifacts["lsa"]
    assert "strategy" in lsa_output, "LSA should produce strategy"
    assert "draft" in lsa_output, "LSA should produce draft"

    draft = lsa_output["draft"]
    assert "client_safe_summary" in draft, "Draft should have client_safe_summary"
    assert len(draft["client_safe_summary"]) > 0, "client_safe_summary should not be empty"
    print(f"  LSA: Draft created with {len(draft['client_safe_summary'])} char summary")

    print("\n=== Integration Test Passed ===\n")
    return True


if __name__ == "__main__":
    result = asyncio.run(test_full_orchestration())
    if result:
        print("✓ All integration tests passed")
