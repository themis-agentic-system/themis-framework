"""Security and authentication for the Themis API."""

from __future__ import annotations

import os

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> str:
    """Verify the API key from the Authorization header.

    Expects: Authorization: Bearer <api-key>

    The API key is validated against the THEMIS_API_KEY environment variable.
    If THEMIS_API_KEY is not set, authentication is disabled (development mode).

    Args:
        credentials: HTTP Bearer credentials from the Authorization header.

    Returns:
        The validated API key.

    Raises:
        HTTPException: If authentication fails or API key is invalid.
    """
    # Check if API key authentication is enabled
    expected_api_key = os.getenv("THEMIS_API_KEY")

    # If no API key is configured, allow all requests (development mode)
    if not expected_api_key:
        return "development-mode"

    # If API key is configured, require authentication
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials. Provide API key via Authorization: Bearer <key>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = credentials.credentials

    # Validate the API key
    if api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return api_key


def is_authentication_enabled() -> bool:
    """Check if API key authentication is enabled.

    Returns:
        True if THEMIS_API_KEY environment variable is set, False otherwise.
    """
    return bool(os.getenv("THEMIS_API_KEY"))
