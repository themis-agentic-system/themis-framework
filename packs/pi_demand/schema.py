"""JSON schema validation for PI demand matter files."""

from __future__ import annotations

from typing import Any

# JSON Schema for PI matter validation
MATTER_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Personal Injury Matter",
    "description": "Schema for personal injury matter files used in the PI demand practice pack",
    "type": "object",
    "properties": {
        "matter": {
            "type": "object",
            "required": ["summary", "parties", "documents"],
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Unique matter identifier"},
                        "title": {"type": "string", "description": "Matter title or case caption"},
                        "jurisdiction": {
                            "type": "string",
                            "enum": ["California", "New York", "Texas", "Florida", "Illinois"],
                            "description": "Jurisdiction where case will be filed"
                        },
                        "cause_of_action": {
                            "type": "string",
                            "enum": [
                                "negligence",
                                "motor_vehicle",
                                "premises_liability",
                                "medical_malpractice",
                                "product_liability",
                                "dog_bite"
                            ],
                            "description": "Primary cause of action type"
                        }
                    }
                },
                "summary": {
                    "type": "string",
                    "minLength": 10,
                    "description": "Brief summary of the matter (required)"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of the matter"
                },
                "parties": {
                    "type": "array",
                    "minItems": 1,
                    "items": {"type": "string"},
                    "description": "List of parties involved (minimum 1 required)"
                },
                "counterparty": {
                    "type": "string",
                    "description": "Name of opposing counsel or defendant"
                },
                "documents": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["title"],
                        "properties": {
                            "title": {"type": "string", "description": "Document title"},
                            "date": {"type": "string", "description": "Document date (YYYY-MM-DD format)"},
                            "summary": {"type": "string", "description": "Document summary"},
                            "content": {"type": "string", "description": "Document content"},
                            "facts": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Key facts from this document"
                            },
                            "type": {"type": "string", "description": "Document type"}
                        }
                    },
                    "description": "Documents related to the matter (minimum 1 required)"
                },
                "events": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["description"],
                        "properties": {
                            "date": {"type": "string", "description": "Event date (YYYY-MM-DD format)"},
                            "description": {"type": "string", "description": "Event description"}
                        }
                    },
                    "description": "Timeline of key events"
                },
                "issues": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"type": "string"},
                            {
                                "type": "object",
                                "required": ["issue"],
                                "properties": {
                                    "issue": {"type": "string", "description": "Legal issue or claim"},
                                    "facts": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Facts supporting this issue"
                                    }
                                }
                            }
                        ]
                    },
                    "description": "Legal issues or causes of action"
                },
                "authorities": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"type": "string"},
                            {
                                "type": "object",
                                "required": ["cite"],
                                "properties": {
                                    "cite": {"type": "string", "description": "Legal citation"},
                                    "summary": {"type": "string", "description": "Authority summary or holding"}
                                }
                            }
                        ]
                    },
                    "description": "Legal authorities (cases, statutes, regulations)"
                },
                "goals": {
                    "type": "object",
                    "properties": {
                        "settlement": {"type": ["string", "number"], "description": "Desired settlement amount"},
                        "fallback": {"type": ["string", "number"], "description": "Minimum acceptable settlement"},
                        "remedy": {"type": "string", "description": "Desired remedy or outcome"}
                    },
                    "description": "Client goals and objectives"
                },
                "strengths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Case strengths and advantages"
                },
                "weaknesses": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Case weaknesses and vulnerabilities"
                },
                "concessions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Potential concessions in negotiation"
                },
                "evidentiary_gaps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Missing evidence or information gaps"
                },
                "confidence_score": {
                    "type": ["integer", "string"],
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Confidence score for case success (0-100)"
                },
                "damages": {
                    "type": "object",
                    "properties": {
                        "specials": {
                            "type": "number",
                            "description": "Economic/special damages (medical, lost wages, etc.)"
                        },
                        "generals": {
                            "type": "number",
                            "description": "Non-economic/general damages (pain & suffering, etc.)"
                        },
                        "punitive": {
                            "type": ["number", "null"],
                            "description": "Punitive damages (if applicable)"
                        }
                    },
                    "description": "Damages breakdown"
                }
            }
        }
    },
    "required": ["matter"]
}


def validate_matter_schema(matter_data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate matter data against schema and return helpful error messages.

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors: list[str] = []

    # Check root structure
    if not isinstance(matter_data, dict):
        errors.append("Matter file must contain a JSON object at the root level.")
        return False, errors

    if "matter" not in matter_data:
        errors.append("Matter file must contain a 'matter' key at the root level.")
        return False, errors

    matter = matter_data["matter"]
    if not isinstance(matter, dict):
        errors.append("The 'matter' value must be an object/dictionary.")
        return False, errors

    # Required fields
    if "summary" not in matter and "description" not in matter:
        errors.append(
            "REQUIRED: Matter must include either a 'summary' or 'description' field (at least 10 characters)."
        )
    elif matter.get("summary"):
        summary = str(matter["summary"])
        if len(summary.strip()) < 10:
            errors.append(
                f"REQUIRED: 'summary' must be at least 10 characters (currently {len(summary.strip())} characters)."
            )

    if "parties" not in matter:
        errors.append(
            "REQUIRED: Matter must include a 'parties' field listing all parties involved."
        )
    elif not isinstance(matter["parties"], list) or len(matter["parties"]) < 1:
        errors.append(
            "REQUIRED: 'parties' must be a list with at least one party."
        )

    if "documents" not in matter:
        errors.append(
            "REQUIRED: Matter must include a 'documents' field with at least one document."
        )
    elif not isinstance(matter["documents"], list) or len(matter["documents"]) < 1:
        errors.append(
            "REQUIRED: 'documents' must be a list with at least one document entry."
        )

    # Validate metadata if present
    if "metadata" in matter:
        metadata = matter["metadata"]
        if not isinstance(metadata, dict):
            errors.append("'metadata' field must be an object/dictionary.")
        else:
            # Validate jurisdiction
            if "jurisdiction" in metadata:
                valid_jurisdictions = ["California", "New York", "Texas", "Florida", "Illinois"]
                if metadata["jurisdiction"] not in valid_jurisdictions:
                    errors.append(
                        f"Invalid jurisdiction '{metadata['jurisdiction']}'. "
                        f"Must be one of: {', '.join(valid_jurisdictions)}"
                    )

            # Validate cause of action
            if "cause_of_action" in metadata:
                valid_causes = [
                    "negligence", "motor_vehicle", "premises_liability",
                    "medical_malpractice", "product_liability", "dog_bite"
                ]
                if metadata["cause_of_action"] not in valid_causes:
                    errors.append(
                        f"Invalid cause_of_action '{metadata['cause_of_action']}'. "
                        f"Must be one of: {', '.join(valid_causes)}"
                    )

    # Validate documents structure
    if "documents" in matter and isinstance(matter["documents"], list):
        for idx, doc in enumerate(matter["documents"], start=1):
            if isinstance(doc, dict):
                if "title" not in doc:
                    errors.append(
                        f"Document #{idx}: Each document must have a 'title' field."
                    )
            elif not isinstance(doc, str):
                errors.append(
                    f"Document #{idx}: Documents must be either strings or objects with a 'title' field."
                )

    # Validate damages structure if present
    if "damages" in matter:
        damages = matter["damages"]
        if not isinstance(damages, dict):
            errors.append("'damages' field must be an object/dictionary.")
        else:
            for key in ["specials", "generals"]:
                if key in damages:
                    try:
                        float(damages[key])
                    except (TypeError, ValueError):
                        errors.append(
                            f"'damages.{key}' must be a number (got: {type(damages[key]).__name__})."
                        )

    # Validate confidence score if present
    if "confidence_score" in matter:
        try:
            score = int(matter["confidence_score"])
            if score < 0 or score > 100:
                errors.append(
                    f"'confidence_score' must be between 0 and 100 (got: {score})."
                )
        except (TypeError, ValueError):
            errors.append(
                f"'confidence_score' must be an integer (got: {matter['confidence_score']})."
            )

    # Warnings (not errors, but helpful info)
    warnings: list[str] = []

    if "metadata" not in matter or "jurisdiction" not in matter.get("metadata", {}):
        warnings.append(
            "RECOMMENDED: Include 'metadata.jurisdiction' for jurisdiction-specific complaint generation."
        )

    if "events" not in matter or not matter.get("events"):
        warnings.append(
            "RECOMMENDED: Include 'events' timeline for better case organization."
        )

    if "issues" not in matter or not matter.get("issues"):
        warnings.append(
            "RECOMMENDED: Include 'issues' to identify legal claims."
        )

    if "goals" not in matter or not matter.get("goals"):
        warnings.append(
            "RECOMMENDED: Include 'goals' (e.g., settlement amount) for strategy development."
        )

    # Append warnings after errors (if any)
    if warnings and not errors:
        errors.extend(["", "=== RECOMMENDATIONS ===" ] + warnings)

    is_valid = len(errors) == 0 or all("RECOMMENDED" in e for e in errors)
    return is_valid, errors


def format_validation_errors(errors: list[str]) -> str:
    """Format validation errors into a user-friendly message."""
    if not errors:
        return "Matter file is valid!"

    lines = ["Matter validation errors:",""]
    for idx, error in enumerate(errors, start=1):
        if error.startswith("===") or error == "":
            lines.append(error)
        else:
            lines.append(f"  {idx}. {error}")

    return "\n".join(lines)
