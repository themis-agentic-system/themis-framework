"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

from typing import Any


import pytest


@pytest.fixture()
def sample_matter() -> dict[str, Any]:
    """Representative payload shared across agent scenarios."""

    return {
        "summary": "Alice retained counsel after Bob failed to deliver contracted goods.",
        "parties": ["Alice", "Bob"],
        "documents": [
            {
                "title": "Master Supply Agreement",
                "content": "Agreement executed on 2023-01-15 for delivery of custom parts.",
                "facts": [
                    "Alice and Bob entered a supply contract on 2023-01-15.",
                    "Bob agreed to deliver custom parts by March 1, 2023.",
                ],
                "date": "2023-01-15",
            },
            {
                "title": "Notice of Breach",
                "summary": "Alice notified Bob of material breach due to non-delivery on March 5, 2023.",
                "facts": [
                    "Alice provided written breach notice on March 5, 2023.",
                    "Bob did not cure within 10 days of notice.",
                ],
                "date": "2023-03-05",
            },
        ],
        "events": [
            {"date": "2023-01-15", "description": "Contract executed."},
            {"date": "2023-03-01", "description": "Delivery deadline passes without shipment."},
            {"date": "2023-03-05", "description": "Notice of breach sent."},
        ],
        "issues": [
            {
                "issue": "Breach of contract",
                "facts": ["Failure to deliver goods by the contractual deadline."],
            },
            "Damages for lost production time",
        ],
        "authorities": [
            {"cite": "Restatement (Second) of Contracts § 235", "summary": "Non-performance is breach."},
            "U.C.C. § 2-601",
        ],
        "goals": {
            "settlement": "Recover $50,000 and secure expedited replacement parts.",
            "fallback": "Seek partial refund and future discount.",
        },
        "strengths": ["Clear written agreement", "Prompt breach notice"],
        "weaknesses": ["Limited documentation of consequential damages"],
        "concessions": ["Extended delivery schedule if partial payment made."],
        "evidentiary_gaps": ["Need expert report on downtime losses."],
        "counterparty": "Bob's Fabrication LLC",
        "confidence_score": 72,
    }

