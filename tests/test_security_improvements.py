"""Tests for security improvements and fixes."""

from __future__ import annotations

import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from api.security import verify_api_key
from orchestrator.models import Matter, MatterWrapper
from orchestrator.router import validate_and_extract_matter


def test_constant_time_api_key_comparison():
    """Verify API key comparison uses constant-time comparison.

    This test ensures the timing attack vulnerability is fixed by checking
    that we use secrets.compare_digest instead of direct string comparison.
    """
    # Import the security module to check implementation
    import inspect

    import api.security as security_module

    # Get the source code of verify_api_key
    source = inspect.getsource(security_module.verify_api_key)

    # Verify that secrets.compare_digest is used
    assert "secrets.compare_digest" in source, "Must use constant-time comparison for API keys"

    # Verify that direct comparison is NOT used for credentials
    # (Allow for other comparisons like is None checks)
    lines = [line.strip() for line in source.split("\n")]
    credential_comparison_lines = [
        line for line in lines
        if "api_key" in line and "==" in line and "expected_api_key" in line
    ]

    # Should not have direct equality comparisons of credentials
    assert len(credential_comparison_lines) == 0, (
        "API key comparison should use secrets.compare_digest, not direct equality"
    )


def test_auth_header_sanitization():
    """Verify authentication headers are sanitized in middleware."""
    # Import middleware to check implementation
    import inspect

    import api.middleware as middleware_module

    # Get source of AuditLoggingMiddleware
    source = inspect.getsource(middleware_module.AuditLoggingMiddleware)

    # Should extract auth_type, not log full auth_header value
    assert "auth_type" in source, "Should extract and log auth type only"

    # Should not log the full auth header value with credentials
    # Check that we don't do: f"...auth_header={auth_header}"
    lines = [line.strip() for line in source.split("\n")]
    dangerous_patterns = [
        line for line in lines
        if "auth_header=" in line and 'f"' in line
    ]

    assert len(dangerous_patterns) == 0, "Should not log full auth_header value"


def test_payload_size_limit_middleware_exists():
    """Verify PayloadSizeLimitMiddleware is implemented."""
    from api.middleware import MAX_REQUEST_SIZE, PayloadSizeLimitMiddleware

    # Verify the middleware class exists
    assert PayloadSizeLimitMiddleware is not None

    # Verify MAX_REQUEST_SIZE is defined and reasonable
    assert MAX_REQUEST_SIZE > 0
    assert MAX_REQUEST_SIZE == 10 * 1024 * 1024, "Should default to 10MB"


def test_matter_validation_with_pydantic():
    """Test Pydantic-based matter validation."""
    # Valid matter
    valid_matter = {
        "summary": "Test case with sufficient detail for summary",
        "parties": ["John Doe", "Jane Smith"],
        "documents": [{"title": "Evidence Doc"}],
    }

    matter = Matter.model_validate(valid_matter)
    assert matter.summary == "Test case with sufficient detail for summary"
    assert len(matter.parties) == 2
    assert len(matter.documents) == 1


def test_matter_validation_rejects_invalid_data():
    """Test that Pydantic validation rejects invalid matter data."""
    from pydantic import ValidationError

    # Missing required field (summary)
    invalid_matter = {
        "parties": ["John Doe"],
        "documents": [{"title": "Doc"}],
    }

    with pytest.raises(ValidationError) as exc_info:
        Matter.model_validate(invalid_matter)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("summary",) for error in errors)


def test_matter_validation_rejects_short_summary():
    """Test that summaries must be at least 10 characters."""
    from pydantic import ValidationError

    invalid_matter = {
        "summary": "Short",  # Only 5 characters
        "parties": ["John Doe"],
        "documents": [{"title": "Doc"}],
    }

    with pytest.raises(ValidationError) as exc_info:
        Matter.model_validate(invalid_matter)

    errors = exc_info.value.errors()
    assert any("at least 10 characters" in str(error["msg"]) for error in errors)


def test_matter_validation_rejects_empty_parties():
    """Test that at least one party is required."""
    from pydantic import ValidationError

    invalid_matter = {
        "summary": "Test case with sufficient detail",
        "parties": [],  # Empty list
        "documents": [{"title": "Doc"}],
    }

    with pytest.raises(ValidationError) as exc_info:
        Matter.model_validate(invalid_matter)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("parties",) for error in errors)


def test_matter_validation_accepts_valid_dates():
    """Test that valid ISO date formats are accepted."""
    valid_matter = {
        "summary": "Test case with date validation",
        "parties": ["John Doe"],
        "documents": [
            {
                "title": "Evidence",
                "date": "2024-01-15",  # Valid ISO format
            }
        ],
        "events": [
            {
                "description": "Incident occurred",
                "date": "2024-01-15",
            }
        ],
    }

    matter = Matter.model_validate(valid_matter)
    assert matter.documents[0]["date"] == "2024-01-15"
    assert matter.events[0].date == "2024-01-15"


def test_matter_validation_rejects_invalid_dates():
    """Test that invalid date formats are rejected."""
    from pydantic import ValidationError

    invalid_matter = {
        "summary": "Test case with invalid date",
        "parties": ["John Doe"],
        "documents": [
            {
                "title": "Evidence",
                "date": "15-01-2024",  # Invalid format
            }
        ],
    }

    with pytest.raises(ValidationError) as exc_info:
        Matter.model_validate(invalid_matter)

    errors = exc_info.value.errors()
    # Should have a date validation error
    assert any("YYYY-MM-DD" in str(error["msg"]) for error in errors)


def test_matter_wrapper_validation():
    """Test MatterWrapper for nested matter structure."""
    wrapped_matter = {
        "matter": {
            "summary": "Test case in wrapper format",
            "parties": ["John Doe"],
            "documents": [{"title": "Doc"}],
        }
    }

    wrapper = MatterWrapper.model_validate(wrapped_matter)
    assert wrapper.matter is not None


def test_validate_and_extract_matter_with_valid_data():
    """Test validate_and_extract_matter with valid matter."""
    matter_data = {
        "matter": {
            "summary": "Test case with valid data",
            "parties": ["John Doe"],
            "documents": [{"title": "Evidence"}],
        }
    }

    result = validate_and_extract_matter(matter_data)
    assert isinstance(result, dict)
    assert result["summary"] == "Test case with valid data"
    assert "parties" in result


def test_validate_and_extract_matter_raises_http_exception_on_invalid():
    """Test that validation raises HTTPException with helpful errors."""
    invalid_matter = {
        "matter": {
            # Missing summary
            "parties": ["John Doe"],
            "documents": [],  # Empty documents (invalid)
        }
    }

    with pytest.raises(HTTPException) as exc_info:
        validate_and_extract_matter(invalid_matter)

    assert exc_info.value.status_code == 422
    assert "Matter validation failed" in str(exc_info.value.detail)


def test_confidence_score_validation():
    """Test that confidence scores must be 0-100."""
    from pydantic import ValidationError

    # Valid confidence score
    valid_matter = {
        "summary": "Test case with confidence score",
        "parties": ["John Doe"],
        "documents": [{"title": "Doc"}],
        "confidence_score": 75,
    }

    matter = Matter.model_validate(valid_matter)
    assert matter.confidence_score == 75

    # Invalid confidence score (> 100)
    invalid_matter = {
        "summary": "Test case with invalid confidence",
        "parties": ["John Doe"],
        "documents": [{"title": "Doc"}],
        "confidence_score": 150,
    }

    with pytest.raises(ValidationError) as exc_info:
        Matter.model_validate(invalid_matter)

    errors = exc_info.value.errors()
    assert any("confidence_score" in str(error["loc"]) for error in errors)


def test_damages_validation():
    """Test that damages must be non-negative."""
    from pydantic import ValidationError

    # Valid damages
    valid_matter = {
        "summary": "Test case with damages",
        "parties": ["John Doe"],
        "documents": [{"title": "Doc"}],
        "damages": {
            "specials": 10000.0,
            "generals": 25000.0,
        },
    }

    matter = Matter.model_validate(valid_matter)
    assert matter.damages is not None

    # Invalid damages (negative)
    invalid_matter = {
        "summary": "Test case with negative damages",
        "parties": ["John Doe"],
        "documents": [{"title": "Doc"}],
        "damages": {
            "specials": -1000.0,  # Negative not allowed
        },
    }

    with pytest.raises(ValidationError) as exc_info:
        Matter.model_validate(invalid_matter)

    errors = exc_info.value.errors()
    assert any("specials" in str(error["loc"]) for error in errors)


def test_api_key_verification_with_valid_key():
    """Test API key verification with valid credentials."""
    # Mock environment and credentials
    with patch.dict(os.environ, {"THEMIS_API_KEY": "test-api-key-123"}):
        # Create mock credentials
        mock_creds = MagicMock()
        mock_creds.credentials = "test-api-key-123"

        # Run async function
        result = asyncio.run(verify_api_key(mock_creds))

        assert result == "test-api-key-123"


def test_api_key_verification_with_invalid_key():
    """Test API key verification rejects invalid keys."""
    with patch.dict(os.environ, {"THEMIS_API_KEY": "test-api-key-123"}):
        mock_creds = MagicMock()
        mock_creds.credentials = "wrong-key"

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(verify_api_key(mock_creds))

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in exc_info.value.detail


def test_api_key_verification_development_mode():
    """Test API key verification in development mode (no key set)."""
    with patch.dict(os.environ, {}, clear=True):
        # Remove THEMIS_API_KEY from environment
        if "THEMIS_API_KEY" in os.environ:
            del os.environ["THEMIS_API_KEY"]

        # Should allow access without credentials
        result = asyncio.run(verify_api_key(None))
        assert result == "development-mode"


if __name__ == "__main__":
    # Run tests directly for debugging
    pytest.main([__file__, "-v"])
