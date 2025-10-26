"""Security and authentication for the Themis API."""

from __future__ import annotations

import os
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


def _load_configured_api_keys() -> list[str]:
    """Load all configured API keys, supporting staged rotations."""

    keys: list[str] = []
    primary = os.getenv("THEMIS_API_KEY")
    if primary:
        keys.append(primary)

    rollover = os.getenv("THEMIS_API_KEY_PREVIOUS")
    if rollover:
        keys.extend(part.strip() for part in rollover.split(",") if part.strip())

    additional = os.getenv("THEMIS_API_KEYS")
    if additional:
        keys.extend(part.strip() for part in additional.split(",") if part.strip())

    # Remove duplicates while preserving order for deterministic behaviour
    seen: set[str] = set()
    unique_keys: list[str] = []
    for key in keys:
        if key not in seen:
            unique_keys.append(key)
            seen.add(key)
    return unique_keys


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
    configured_keys = _load_configured_api_keys()

    # If no API key is configured, allow all requests (development mode)
    if not configured_keys:
        return "development-mode"

    # If API key is configured, require authentication
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials. Provide API key via Authorization: Bearer <key>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = credentials.credentials

    # Validate against all configured keys using constant-time comparison to
    # avoid leaking timing information that could aid attackers during key
    # rotation windows.
    for expected in configured_keys:
        if secrets.compare_digest(api_key, expected):
            return api_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "Bearer"},
    )


def is_authentication_enabled() -> bool:
    """Check if API key authentication is enabled.

    Returns:
        True if THEMIS_API_KEY environment variable is set, False otherwise.
    """
    return bool(_load_configured_api_keys())
