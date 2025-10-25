"""JSON schema validation for criminal defense matter files."""

from __future__ import annotations

from typing import Any

# JSON Schema for Criminal Defense matter validation
MATTER_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Criminal Defense Matter",
    "description": "Schema for state criminal defense matter files",
    "type": "object",
    "properties": {
        "matter": {
            "type": "object",
            "required": ["client", "charges", "arrest"],
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "case_number": {"type": "string", "description": "Court case number"},
                        "jurisdiction": {"type": "string", "description": "State/jurisdiction (e.g., California, New York)"},
                        "court": {"type": "string", "description": "Court name"},
                        "case_type": {
                            "type": "string",
                            "enum": ["felony", "misdemeanor"],
                            "description": "Felony or misdemeanor classification"
                        },
                        "id": {"type": "string", "description": "Unique matter identifier"}
                    }
                },
                "client": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string", "description": "Client name"},
                        "dob": {"type": "string", "description": "Date of birth (YYYY-MM-DD)"},
                        "prior_record": {
                            "type": "string",
                            "enum": ["none", "misdemeanor", "felony"],
                            "description": "Prior criminal record"
                        }
                    }
                },
                "charges": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["statute", "description"],
                        "properties": {
                            "statute": {"type": "string", "description": "Statute citation"},
                            "description": {"type": "string", "description": "Charge description"},
                            "degree": {
                                "type": "string",
                                "enum": ["felony", "misdemeanor", "infraction"],
                                "description": "Charge classification"
                            },
                            "potential_sentence": {"type": "string", "description": "Potential sentencing range"}
                        }
                    },
                    "description": "Criminal charges filed"
                },
                "arrest": {
                    "type": "object",
                    "required": ["date"],
                    "properties": {
                        "date": {"type": "string", "description": "Arrest date/time (YYYY-MM-DD or ISO format)"},
                        "location": {"type": "string", "description": "Arrest location"},
                        "arresting_agency": {"type": "string", "description": "Law enforcement agency"},
                        "officers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Arresting officers"
                        },
                        "circumstances": {"type": "string", "description": "Circumstances of arrest"}
                    }
                },
                "search_and_seizure": {
                    "type": "object",
                    "properties": {
                        "was_search_conducted": {"type": "boolean"},
                        "search_type": {
                            "type": "string",
                            "enum": ["warrant", "consent", "incident_to_arrest", "automobile", "plain_view", "exigent", "none"],
                            "description": "Type of search conducted"
                        },
                        "warrant_number": {"type": "string", "description": "Search warrant number"},
                        "items_seized": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Items seized during search"
                        },
                        "location_searched": {"type": "string", "description": "Location of search"}
                    }
                },
                "interrogation": {
                    "type": "object",
                    "properties": {
                        "was_interrogated": {"type": "boolean"},
                        "miranda_given": {"type": "boolean"},
                        "miranda_waived": {"type": "boolean"},
                        "statements_made": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Statements made by defendant"
                        },
                        "interrogation_location": {"type": "string"},
                        "duration": {"type": "string", "description": "Duration of interrogation"},
                        "officers_present": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "identification": {
                    "type": "object",
                    "properties": {
                        "identification_procedure": {
                            "type": "string",
                            "enum": ["lineup", "showup", "photo_array", "none"],
                            "description": "Type of identification procedure"
                        },
                        "was_counsel_present": {"type": "boolean"},
                        "witness_confidence": {
                            "type": "string",
                            "enum": ["certain", "fairly_certain", "uncertain"]
                        }
                    }
                },
                "discovery_received": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "document_type": {"type": "string"},
                            "date_received": {"type": "string"},
                            "summary": {"type": "string"}
                        }
                    },
                    "description": "Discovery already received from prosecution"
                },
                "discovery_outstanding": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Discovery still needed"
                },
                "constitutional_issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issue_type": {
                                "type": "string",
                                "enum": ["fourth_amendment", "fifth_amendment", "sixth_amendment", "other"]
                            },
                            "description": {"type": "string"},
                            "evidence": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    },
                    "description": "Constitutional issues identified"
                },
                "defense_theory": {"type": "string", "description": "Primary defense theory"},
                "goals": {
                    "type": "object",
                    "properties": {
                        "primary": {"type": "string", "description": "Primary goal (e.g., dismissal, acquittal)"},
                        "secondary": {"type": "string", "description": "Secondary goal"},
                        "fallback": {"type": "string", "description": "Fallback position"}
                    }
                },
                "client_narrative": {"type": "string", "description": "Client's version of events"}
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
    if "client" not in matter:
        errors.append("REQUIRED: Matter must include a 'client' field with client information.")
    elif not isinstance(matter["client"], dict):
        errors.append("REQUIRED: 'client' must be an object/dictionary.")
    elif "name" not in matter["client"]:
        errors.append("REQUIRED: 'client.name' is required.")

    if "charges" not in matter:
        errors.append("REQUIRED: Matter must include a 'charges' field listing all charges.")
    elif not isinstance(matter["charges"], list) or len(matter["charges"]) < 1:
        errors.append("REQUIRED: 'charges' must be a list with at least one charge.")
    else:
        for idx, charge in enumerate(matter["charges"], start=1):
            if not isinstance(charge, dict):
                errors.append(f"Charge #{idx}: Must be an object/dictionary.")
            else:
                if "statute" not in charge:
                    errors.append(f"Charge #{idx}: Missing required 'statute' field.")
                if "description" not in charge:
                    errors.append(f"Charge #{idx}: Missing required 'description' field.")

    if "arrest" not in matter:
        errors.append("REQUIRED: Matter must include an 'arrest' field with arrest information.")
    elif not isinstance(matter["arrest"], dict):
        errors.append("REQUIRED: 'arrest' must be an object/dictionary.")
    elif "date" not in matter["arrest"]:
        errors.append("REQUIRED: 'arrest.date' is required.")

    # Warnings (not errors, but helpful info)
    warnings: list[str] = []

    if "metadata" not in matter or "jurisdiction" not in matter.get("metadata", {}):
        warnings.append(
            "RECOMMENDED: Include 'metadata.jurisdiction' for jurisdiction-specific discovery and motion generation."
        )

    if "metadata" not in matter or "case_type" not in matter.get("metadata", {}):
        warnings.append(
            "RECOMMENDED: Include 'metadata.case_type' (felony/misdemeanor) for accurate analysis."
        )

    if "constitutional_issues" not in matter or not matter.get("constitutional_issues"):
        warnings.append(
            "RECOMMENDED: Include 'constitutional_issues' if you've identified Fourth/Fifth/Sixth Amendment concerns."
        )

    if "defense_theory" not in matter or not matter.get("defense_theory"):
        warnings.append(
            "RECOMMENDED: Include 'defense_theory' to guide case strategy."
        )

    if "discovery_outstanding" not in matter or not matter.get("discovery_outstanding"):
        warnings.append(
            "RECOMMENDED: Include 'discovery_outstanding' to track needed evidence."
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

    lines = ["Matter validation errors:", ""]
    for idx, error in enumerate(errors, start=1):
        if error.startswith("===") or error == "":
            lines.append(error)
        else:
            lines.append(f"  {idx}. {error}")

    return "\n".join(lines)
