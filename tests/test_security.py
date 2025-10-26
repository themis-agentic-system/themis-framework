from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from api.security import is_authentication_enabled, verify_api_key


@pytest.mark.asyncio
async def test_verify_api_key_development_mode_when_unset() -> None:
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="anything")
    result = await verify_api_key(credentials)
    assert result == "development-mode"
    assert is_authentication_enabled() is False


@pytest.mark.asyncio
async def test_verify_api_key_accepts_primary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("THEMIS_API_KEY", "current-key")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="current-key")
    assert await verify_api_key(credentials) == "current-key"
    assert is_authentication_enabled() is True


@pytest.mark.asyncio
async def test_verify_api_key_supports_rotation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("THEMIS_API_KEY", "new-key")
    monkeypatch.setenv("THEMIS_API_KEY_PREVIOUS", "old-key")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="old-key")
    assert await verify_api_key(credentials) == "old-key"


@pytest.mark.asyncio
async def test_verify_api_key_rejects_invalid_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("THEMIS_API_KEY", "expected")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="wrong")
    with pytest.raises(HTTPException) as exc:
        await verify_api_key(credentials)
    assert exc.value.status_code == 401
