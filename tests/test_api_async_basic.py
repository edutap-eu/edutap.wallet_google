"""Basic tests for async API to verify it works."""

import pytest


@pytest.mark.asyncio
async def test_new_is_sync():
    """Test that new() is still synchronous (no async needed for model creation)."""
    from edutap.wallet_google import api

    # new() should be synchronous - it just creates a model instance
    result = api.new("GenericClass", {"id": "test.123"})
    assert result.id == "test.123"


@pytest.mark.asyncio
async def test_imports_work():
    """Test that async API functions exist in the api module."""
    from edutap.wallet_google import api
    from edutap.wallet_google import session

    # Verify sync functions exist
    assert hasattr(api, "create")
    assert hasattr(api, "read")
    assert hasattr(api, "update")
    assert hasattr(api, "message")
    assert hasattr(api, "listing")

    # Verify async functions exist with 'a' prefix
    assert hasattr(api, "acreate")
    assert hasattr(api, "aread")
    assert hasattr(api, "aupdate")
    assert hasattr(api, "amessage")
    assert hasattr(api, "alisting")

    assert hasattr(session, "session_manager")
    assert hasattr(session, "SessionManager")


@pytest.mark.asyncio
async def test_validate_async_functions_exist():
    """Test that async validation functions exist."""
    from edutap.wallet_google.handlers import validate

    assert hasattr(validate, "google_root_signing_public_keys_async")
    assert hasattr(validate, "verified_signed_message_async")
