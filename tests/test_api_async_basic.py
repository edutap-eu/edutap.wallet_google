"""Basic tests for async API to verify it works."""

import pytest


@pytest.mark.asyncio
async def test_new_is_sync():
    """Test that new() is still synchronous (no async needed for model creation)."""
    from edutap.wallet_google import api_async

    # new() should be synchronous - it just creates a model instance
    result = api_async.new("GenericClass", {"id": "test.123"})
    assert result.id == "test.123"


@pytest.mark.asyncio
async def test_imports_work():
    """Test that async modules can be imported."""
    from edutap.wallet_google import api_async
    from edutap.wallet_google import session_async

    # Verify the modules exist and have expected attributes
    assert hasattr(api_async, "create")
    assert hasattr(api_async, "read")
    assert hasattr(api_async, "update")
    assert hasattr(api_async, "message")
    assert hasattr(api_async, "listing")

    assert hasattr(session_async, "session_manager_async")
    assert hasattr(session_async, "AsyncSessionManager")


@pytest.mark.asyncio
async def test_validate_async_functions_exist():
    """Test that async validation functions exist."""
    from edutap.wallet_google.handlers import validate

    assert hasattr(validate, "google_root_signing_public_keys_async")
    assert hasattr(validate, "verified_signed_message_async")
