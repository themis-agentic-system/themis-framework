"""Pydantic models for matter validation and type safety."""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Document(BaseModel):
    """Document in a legal matter."""

    title: str = Field(..., min_length=1, description="Document title")
    date: str | None = Field(None, description="Document date (YYYY-MM-DD format)")
    summary: str | None = Field(None, description="Document summary")
    content: str | None = Field(None, description="Document content")
    facts: list[str] = Field(default_factory=list, description="Key facts from document")
    type: str | None = Field(None, description="Document type")

    def __getitem__(self, item: str) -> Any:
        """Provide dict-style access for backwards compatibility."""

        try:
            return getattr(self, item)
        except AttributeError as exc:
            raise KeyError(item) from exc

    def get(self, item: str, default: Any = None) -> Any:
        """Return a value using dict-style semantics."""

        return getattr(self, item, default)

    def keys(self) -> list[str]:
        """Expose field names similar to a mapping."""

        return list(self.model_fields)

    def items(self) -> list[tuple[str, Any]]:
        """Iterate over key/value pairs."""

        return [(key, getattr(self, key)) for key in self.model_fields]

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        """Validate date format if provided."""
        if v is not None and v:
            try:
                # Validate it's a proper date format
                date.fromisoformat(v)
            except ValueError as exc:
                raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}") from exc
        return v


class Event(BaseModel):
    """Event in a legal matter timeline."""

    date: str | None = Field(None, description="Event date (YYYY-MM-DD format)")
    description: str = Field(..., min_length=1, description="Event description")

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        """Validate date format if provided."""
        if v is not None and v:
            try:
                date.fromisoformat(v)
            except ValueError as exc:
                raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}") from exc
        return v


class Issue(BaseModel):
    """Legal issue or claim."""

    issue: str = Field(..., min_length=1, description="Legal issue description")
    facts: list[str] = Field(default_factory=list, description="Supporting facts")
    area_of_law: str | None = Field(None, description="Area of law")
    strength: str | None = Field(None, description="Strength of issue")


class Authority(BaseModel):
    """Legal authority (case, statute, regulation)."""

    cite: str = Field(..., min_length=1, description="Legal citation")
    summary: str | None = Field(None, description="Authority summary or holding")


class Goals(BaseModel):
    """Client goals and objectives."""

    settlement: str | float | None = Field(None, description="Desired settlement amount")
    fallback: str | float | None = Field(None, description="Minimum acceptable settlement")
    remedy: str | None = Field(None, description="Desired remedy or outcome")
    ideal: str | None = Field(None, description="Ideal outcome")
    minimum: str | None = Field(None, description="Minimum acceptable outcome")
    opening: str | None = Field(None, description="Opening position")


class Damages(BaseModel):
    """Damages breakdown."""

    specials: float | None = Field(None, ge=0, description="Economic/special damages")
    generals: float | None = Field(None, ge=0, description="Non-economic/general damages")
    punitive: float | None = Field(None, ge=0, description="Punitive damages")


class Metadata(BaseModel):
    """Matter metadata."""

    id: str | None = Field(None, description="Unique matter identifier")
    title: str | None = Field(None, description="Matter title or case caption")
    jurisdiction: str | None = Field(None, description="Jurisdiction")
    cause_of_action: str | None = Field(None, description="Primary cause of action")
    case_number: str | None = Field(None, description="Case number")
    filing_date: str | None = Field(None, description="Filing date")


class Matter(BaseModel):
    """Legal matter payload with comprehensive validation.

    This model provides type safety and validation for matter payloads
    passed to the orchestrator and agents.
    """

    summary: str = Field(..., min_length=10, description="Brief summary of the matter")
    parties: list[str] = Field(
        ..., min_length=1, description="List of parties involved"
    )
    documents: list[Document | dict[str, Any]] = Field(
        ..., min_length=1, description="Documents related to the matter"
    )

    # Optional fields
    metadata: Metadata | dict[str, Any] | None = Field(None, description="Matter metadata")
    description: str | None = Field(None, description="Detailed description")
    counterparty: str | None = Field(None, description="Opposing party or counsel")
    events: list[Event | dict[str, Any]] = Field(default_factory=list, description="Timeline events")
    issues: list[Issue | dict[str, Any] | str] = Field(
        default_factory=list, description="Legal issues or claims"
    )
    authorities: list[Authority | dict[str, Any] | str] = Field(
        default_factory=list, description="Legal authorities"
    )
    goals: Goals | dict[str, Any] | None = Field(None, description="Client goals")
    strengths: list[str] = Field(default_factory=list, description="Case strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Case weaknesses")
    concessions: list[str] = Field(default_factory=list, description="Potential concessions")
    evidentiary_gaps: list[str] = Field(default_factory=list, description="Evidence gaps")
    confidence_score: int | None = Field(None, ge=0, le=100, description="Confidence score (0-100)")
    damages: Damages | dict[str, Any] | None = Field(None, description="Damages breakdown")

    # Allow additional fields for flexibility
    model_config = {"extra": "allow"}

    @field_validator("summary")
    @classmethod
    def validate_summary_length(cls, v: str) -> str:
        """Ensure summary is meaningful."""
        if len(v.strip()) < 10:
            raise ValueError(f"Summary must be at least 10 characters, got: {len(v.strip())}")
        return v.strip()

    @field_validator("parties")
    @classmethod
    def validate_parties_not_empty(cls, v: list[str]) -> list[str]:
        """Ensure at least one party is provided."""
        if not v:
            raise ValueError("At least one party must be specified")
        # Remove empty strings
        parties = [p.strip() for p in v if p.strip()]
        if not parties:
            raise ValueError("At least one non-empty party must be specified")
        return parties

    @field_validator("documents")
    @classmethod
    def validate_documents_not_empty(cls, v: list[Document | dict[str, Any]]) -> list[Document | dict[str, Any]]:
        """Ensure at least one document is provided."""
        if not v:
            raise ValueError("At least one document must be provided")
        return v

    @field_validator("documents", mode="before")
    @classmethod
    def coerce_documents(cls, value: Any) -> Any:
        """Coerce raw mappings into Document models before validation."""

        if value is None:
            return value
        if not isinstance(value, list):
            raise TypeError("Documents must be provided as a list")
        coerced: list[Document] = []
        for entry in value:
            if isinstance(entry, Document):
                coerced.append(entry)
            elif isinstance(entry, dict):
                coerced.append(Document.model_validate(entry))
            else:
                raise TypeError("Documents must be dictionaries or Document instances")
        return coerced

    @field_validator("events", mode="before")
    @classmethod
    def coerce_events(cls, value: Any) -> Any:
        """Ensure events are validated Event models."""

        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("Events must be provided as a list")
        coerced: list[Event] = []
        for entry in value:
            if isinstance(entry, Event):
                coerced.append(entry)
            elif isinstance(entry, dict):
                coerced.append(Event.model_validate(entry))
            else:
                raise TypeError("Events must be dictionaries or Event instances")
        return coerced

    @field_validator("issues", mode="before")
    @classmethod
    def coerce_issues(cls, value: Any) -> Any:
        """Normalise issues into Issue models."""

        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("Issues must be provided as a list")
        coerced: list[Issue] = []
        for entry in value:
            if isinstance(entry, Issue):
                coerced.append(entry)
            elif isinstance(entry, dict):
                coerced.append(Issue.model_validate(entry))
            elif isinstance(entry, str):
                coerced.append(Issue.model_validate({"issue": entry}))
            else:
                raise TypeError("Issues must be strings, dictionaries, or Issue instances")
        return coerced

    @field_validator("authorities", mode="before")
    @classmethod
    def coerce_authorities(cls, value: Any) -> Any:
        """Normalise authorities into Authority models."""

        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("Authorities must be provided as a list")
        coerced: list[Authority] = []
        for entry in value:
            if isinstance(entry, Authority):
                coerced.append(entry)
            elif isinstance(entry, dict):
                coerced.append(Authority.model_validate(entry))
            elif isinstance(entry, str):
                coerced.append(Authority.model_validate({"cite": entry}))
            else:
                raise TypeError("Authorities must be strings, dictionaries, or Authority instances")
        return coerced

    @field_validator("damages", mode="before")
    @classmethod
    def coerce_damages(cls, value: Any) -> Any:
        """Coerce damages payloads into Damages models."""

        if value is None or isinstance(value, Damages):
            return value
        if isinstance(value, dict):
            return Damages.model_validate(value)
        raise TypeError("Damages must be a mapping of numeric values")

    @field_validator("metadata", mode="before")
    @classmethod
    def coerce_metadata(cls, value: Any) -> Any:
        """Coerce metadata payloads into Metadata models."""

        if value is None or isinstance(value, Metadata):
            return value
        if isinstance(value, dict):
            return Metadata.model_validate(value)
        raise TypeError("Metadata must be provided as a mapping")

    @field_validator("goals", mode="before")
    @classmethod
    def coerce_goals(cls, value: Any) -> Any:
        """Coerce goals payloads into Goals models."""

        if value is None or isinstance(value, Goals):
            return value
        if isinstance(value, dict):
            return Goals.model_validate(value)
        raise TypeError("Goals must be provided as a mapping")


class MatterWrapper(BaseModel):
    """Wrapper for matter payloads to match existing JSON structure.

    Many existing fixtures use {"matter": {...}} structure, so we support that.
    """

    matter: Matter | dict[str, Any] = Field(..., description="The legal matter data")

    model_config = {"extra": "forbid"}
