"""Edge case testing for agent signal propagation."""

import asyncio

from agents.dea import DEAAgent
from agents.lsa import LSAAgent


def test_dea_with_no_citations():
    """Test DEA agent when no citations are found."""
    agent = DEAAgent()
    matter = {
        "summary": "Test case with no authorities",
        "parties": ["Alice", "Bob"],
        "issues": ["Test issue"],
        "authorities": [],  # Empty authorities
    }

    result = asyncio.run(agent.run(matter))

    # Should still provide the authorities signal structure
    assert "authorities" in result
    assert "controlling_authorities" in result["authorities"]
    assert "contrary_authorities" in result["authorities"]

    # Contrary authorities should have the placeholder message
    assert len(result["authorities"]["contrary_authorities"]) > 0
    assert "None identified" in result["authorities"]["contrary_authorities"][0]

    print("✓ DEA handles empty citations correctly")


def test_lsa_with_minimal_strategy():
    """Test LSA agent with minimal strategy data."""
    agent = LSAAgent()
    matter = {
        "summary": "Minimal test case",
        "parties": ["Alice"],
        "goals": {},
    }

    result = asyncio.run(agent.run(matter))

    # Should still provide draft with client_safe_summary
    assert "draft" in result
    assert "client_safe_summary" in result["draft"]
    assert len(result["draft"]["client_safe_summary"]) > 0

    # Should have risk_level
    assert "risk_level" in result["draft"]
    assert result["draft"]["risk_level"] in ["low", "moderate", "high"]

    print("✓ LSA handles minimal strategy correctly")


def test_dea_authorities_signal_structure():
    """Test that DEA returns proper signal structure."""
    agent = DEAAgent()
    matter = {
        "summary": "Test",
        "parties": ["Alice"],
        "issues": [{"issue": "Negligence", "facts": ["Test fact"]}],
        "authorities": [
            {"cite": "Smith v. Jones", "summary": "Test case"},
            {"cite": "Doe v. Roe", "summary": "Another case"},
        ],
    }

    result = asyncio.run(agent.run(matter))

    # Check signal structure
    assert "authorities" in result
    authorities = result["authorities"]

    # Should be a dict with both keys
    assert isinstance(authorities, dict)
    assert "controlling_authorities" in authorities
    assert "contrary_authorities" in authorities

    # Controlling authorities should be a list
    assert isinstance(authorities["controlling_authorities"], list)
    assert len(authorities["controlling_authorities"]) == 2

    # Contrary authorities should have placeholder
    assert isinstance(authorities["contrary_authorities"], list)
    assert len(authorities["contrary_authorities"]) > 0

    print("✓ DEA authorities signal structure is correct")


def test_lsa_draft_signal_with_empty_objectives():
    """Test LSA draft generation with empty objectives."""
    agent = LSAAgent()
    matter = {
        "summary": "Test",
        "parties": ["Alice"],
        "goals": {},
    }

    result = asyncio.run(agent.run(matter))

    # Should still create a draft
    assert "draft" in result
    draft = result["draft"]

    # client_safe_summary should exist even with empty objectives
    assert "client_safe_summary" in draft
    assert isinstance(draft["client_safe_summary"], str)
    assert len(draft["client_safe_summary"]) > 0

    # Should contain confidence percentage
    assert "%" in draft["client_safe_summary"]

    print("✓ LSA creates draft with empty objectives")


if __name__ == "__main__":
    print("\n=== Testing Edge Cases ===\n")

    test_dea_with_no_citations()
    test_lsa_with_minimal_strategy()
    test_dea_authorities_signal_structure()
    test_lsa_draft_signal_with_empty_objectives()

    print("\n=== All Edge Case Tests Passed ===\n")
