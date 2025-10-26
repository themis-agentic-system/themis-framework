from __future__ import annotations

from orchestrator.router import sanitize_matter_payload, validate_and_extract_matter


def _valid_matter(summary: str) -> dict[str, object]:
    return {
        "summary": summary,
        "parties": ["Alice", "Bob"],
        "documents": [
            {
                "title": "Complaint",
                "summary": "Complaint summary",
                "date": "2024-01-01",
            }
        ],
    }


def test_validate_and_extract_matter_sanitises_script_tags() -> None:
    payload = _valid_matter("Legitimate <script>alert('x')</script> summary text")
    validated = validate_and_extract_matter(payload)
    assert "<script" not in validated["summary"]
    assert "alert" not in validated["summary"]
    assert validated["summary"].startswith("Legitimate")


def test_sanitize_matter_payload_truncates_long_strings() -> None:
    long_text = "a" * 15000
    result = sanitize_matter_payload(long_text)
    assert len(result) == 10000


def test_sanitize_matter_payload_removes_control_characters() -> None:
    dirty = "Important\x00 information\x07"
    result = sanitize_matter_payload({"notes": dirty})
    assert result["notes"] == "Important information"
