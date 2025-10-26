"""Model fact patterns for reference and testing."""

from __future__ import annotations

FACT_PATTERNS = {
    "rear_end": {
        "title": "Rear-end collision at controlled intersection",
        "facts": [
            "Defendant failed to stop at a red light and struck Plaintiff's vehicle.",
            "Plaintiff experienced immediate neck and back pain.",
            "Police report cites Defendant for inattentive driving.",
        ],
        "damages": {
            "specials": 18500,
            "generals": 45000,
        },
    },
    "premises_trip": {
        "title": "Trip and fall in retail store",
        "facts": [
            "Plaintiff tripped over unsecured mat near store entrance.",
            "Security footage shows mat folding over multiple times that day.",
            "Store log lacks inspection for more than two hours prior to incident.",
        ],
        "damages": {
            "specials": 32000,
            "generals": 60000,
        },
    },
}
