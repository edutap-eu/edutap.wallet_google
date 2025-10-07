"""Comprehensive tests for async API CRUD operations."""

from edutap.wallet_google import api
from edutap.wallet_google.exceptions import ObjectAlreadyExistsException
from edutap.wallet_google.exceptions import QuotaExceededException
from edutap.wallet_google.exceptions import WalletException
from edutap.wallet_google.models.datatypes import enums
from edutap.wallet_google.session import session_manager

import httpx
import pytest
import respx


@pytest.fixture
def mock_async_session(monkeypatch):
    """Fixture to provide a mock async session that doesn't require real credentials."""
    from edutap.wallet_google.session import SessionManager

    def mock_async_session(self, credentials=None):
        # Return httpx.AsyncClient without real auth
        # We just need something that httpx/respx can mock
        return httpx.AsyncClient()

    monkeypatch.setattr(SessionManager, "async_session", mock_async_session)
    yield


@pytest.mark.asyncio
@respx.mock
async def test_create_generic_class(mock_async_session):
    """Test creating a GenericClass via async API."""
    name = "GenericClass"
    class_id = "test.class.123"
    url = session_manager.url(name)

    # Mock the POST request
    respx.post(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": class_id,
                "enableSmartTap": False,
                "multipleDevicesAndHoldersAllowedStatus": "STATUS_UNSPECIFIED",
                "viewUnlockRequirement": "VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED",
            },
        )
    )

    data = api.new(
        name,
        {
            "id": class_id,
            "enableSmartTap": False,
            "multipleDevicesAndHoldersAllowedStatus": enums.MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED,
            "viewUnlockRequirement": enums.ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED,
        },
    )
    result = await api.acreate(data)

    assert result.id == class_id
    assert result.enableSmartTap is False


@pytest.mark.asyncio
@respx.mock
async def test_create_generic_object(mock_async_session):
    """Test creating a GenericObject via async API."""
    name = "GenericObject"
    object_id = "test.object.123"
    class_id = "test.class.123"
    url = session_manager.url(name)

    # Mock the POST request
    respx.post(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": object_id,
                "classId": class_id,
                "state": "ACTIVE",
            },
        )
    )

    data = api.new(
        name,
        {
            "id": object_id,
            "classId": class_id,
            "state": enums.State.ACTIVE,
        },
    )
    result = await api.acreate(data)

    assert result.id == object_id
    assert result.classId == class_id
    assert result.state == enums.State.ACTIVE


@pytest.mark.asyncio
@respx.mock
async def test_create_409_already_exists(mock_async_session):
    """Test that create raises ObjectAlreadyExistsException on 409."""
    name = "GenericClass"
    class_id = "test.class.existing"
    url = session_manager.url(name)

    # Mock a 409 response
    respx.post(url).mock(
        return_value=httpx.Response(
            409,
            json={
                "error": {
                    "code": 409,
                    "message": "Resource already exists",
                    "status": "ALREADY_EXISTS",
                }
            },
        )
    )

    data = api.new(name, {"id": class_id})

    with pytest.raises(ObjectAlreadyExistsException) as exc_info:
        await api.acreate(data)

    assert class_id in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_read_generic_class(mock_async_session):
    """Test reading a GenericClass via async API."""
    name = "GenericClass"
    class_id = "test.class.123"
    url = session_manager.url(name, f"/{class_id}")

    # Mock the GET request
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": class_id,
                "enableSmartTap": True,
            },
        )
    )

    result = await api.aread(name, class_id)

    assert result.id == class_id
    assert result.enableSmartTap is True


@pytest.mark.asyncio
@respx.mock
async def test_read_404_not_found(mock_async_session):
    """Test that read raises LookupError on 404."""
    name = "GenericClass"
    class_id = "test.class.nonexistent"
    url = session_manager.url(name, f"/{class_id}")

    # Mock a 404 response
    respx.get(url).mock(
        return_value=httpx.Response(
            404,
            json={
                "error": {
                    "code": 404,
                    "message": "Resource not found",
                    "status": "NOT_FOUND",
                }
            },
        )
    )

    with pytest.raises(LookupError) as exc_info:
        await api.aread(name, class_id)

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_read_403_quota_exceeded(mock_async_session):
    """Test that read raises QuotaExceededException when quota is exceeded."""
    name = "GenericObject"
    resource_id = "test.resource.id"
    url = session_manager.url(name, f"/{resource_id}")

    # Mock a 403 response with quota error message
    respx.get(url).mock(
        return_value=httpx.Response(
            403,
            json={
                "error": {
                    "code": 403,
                    "message": "Quota exceeded for quota metric 'Read requests'",
                    "status": "RESOURCE_EXHAUSTED",
                }
            },
        )
    )

    with pytest.raises(QuotaExceededException) as exc_info:
        await api.aread(name, resource_id)

    assert "Quota exceeded while trying to read" in str(exc_info.value)
    assert resource_id in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_read_403_permission_denied(mock_async_session):
    """Test that read raises WalletException when access is denied."""
    name = "GenericObject"
    resource_id = "test.resource.id"
    url = session_manager.url(name, f"/{resource_id}")

    # Mock a 403 response with permission denied message
    respx.get(url).mock(
        return_value=httpx.Response(
            403,
            json={
                "error": {
                    "code": 403,
                    "message": "The caller does not have permission",
                    "status": "PERMISSION_DENIED",
                }
            },
        )
    )

    with pytest.raises(WalletException) as exc_info:
        await api.aread(name, resource_id)

    # Should NOT be QuotaExceededException
    assert not isinstance(exc_info.value, QuotaExceededException)
    assert "Access denied while trying to read" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_update_generic_object_partial(mock_async_session):
    """Test partial update of a GenericObject via async API."""
    name = "GenericObject"
    object_id = "test.object.123"
    url = session_manager.url(name, f"/{object_id}")

    # Mock the PATCH request
    respx.patch(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": object_id,
                "classId": "test.class.123",
                "state": "EXPIRED",
            },
        )
    )

    data = api.new(
        name,
        {
            "id": object_id,
            "classId": "test.class.123",
            "state": enums.State.EXPIRED,
        },
    )
    result = await api.aupdate(data, partial=True)

    assert result.id == object_id
    assert result.state == enums.State.EXPIRED


@pytest.mark.asyncio
@respx.mock
async def test_update_generic_object_full(mock_async_session):
    """Test full update of a GenericObject via async API."""
    name = "GenericObject"
    object_id = "test.object.123"
    url = session_manager.url(name, f"/{object_id}")

    # Mock the PUT request
    respx.put(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": object_id,
                "classId": "test.class.123",
                "state": "INACTIVE",
            },
        )
    )

    data = api.new(
        name,
        {
            "id": object_id,
            "classId": "test.class.123",
            "state": enums.State.INACTIVE,
        },
    )
    result = await api.aupdate(data, partial=False)

    assert result.id == object_id
    assert result.state == enums.State.INACTIVE


@pytest.mark.asyncio
@respx.mock
async def test_message_generic_object(mock_async_session):
    """Test sending a message to a GenericObject via async API."""
    name = "GenericObject"
    object_id = "test.object.123"
    url = session_manager.url(name, f"/{object_id}/addMessage")

    # Mock the POST request
    respx.post(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "resource": {
                    "id": object_id,
                    "classId": "test.class.123",
                    "state": "ACTIVE",
                }
            },
        )
    )

    result = await api.amessage(
        name,
        object_id,
        {
            "header": "Test Header",
            "body": "Test message body",
        },
    )

    assert result.id == object_id


@pytest.mark.asyncio
@respx.mock
async def test_listing_generic_classes(mock_async_session):
    """Test listing GenericClasses via async API."""
    name = "GenericClass"
    issuer_id = "1234567890"
    url = session_manager.url(name)

    # Mock the GET request for listing
    respx.get(url, params={"issuerId": issuer_id}).mock(
        return_value=httpx.Response(
            200,
            json={
                "resources": [
                    {"id": f"{issuer_id}.class1"},
                    {"id": f"{issuer_id}.class2"},
                ]
            },
        )
    )

    results = []
    async for item in api.alisting(name, issuer_id=issuer_id):
        results.append(item)

    assert len(results) == 2
    assert results[0].id == f"{issuer_id}.class1"
    assert results[1].id == f"{issuer_id}.class2"


@pytest.mark.asyncio
@respx.mock
async def test_listing_empty_result(mock_async_session):
    """Test listing with empty results via async API."""
    name = "GenericObject"
    class_id = "test.class.empty"
    url = session_manager.url(name)

    # Mock empty result
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={"resources": []},
        )
    )

    results = []
    async for item in api.alisting(name, resource_id=class_id):
        results.append(item)

    assert len(results) == 0
