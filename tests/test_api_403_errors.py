from edutap.wallet_google.api import create
from edutap.wallet_google.api import message
from edutap.wallet_google.api import new
from edutap.wallet_google.api import read
from edutap.wallet_google.api import update
from edutap.wallet_google.clientpool import client_pool
from edutap.wallet_google.exceptions import QuotaExceededException
from edutap.wallet_google.exceptions import WalletException
from edutap.wallet_google.models.datatypes import enums

import httpx
import pytest
import respx

# this tests relates to reproduce issue https://github.com/edutap-eu/edutap.wallet_google/issues/36


@respx.mock
def test_read_403_quota_exceeded(mock_session):
    """Test that read() raises QuotaExceededException when quota is exceeded."""
    name = "GenericObject"
    resource_id = "test.resource.id"
    url = client_pool.url(name, f"/{resource_id}")

    # Mock a 403 response with quota error message
    respx.get(url).mock(
        return_value=httpx.Response(
            403,
            json={
                "error": {
                    "code": 403,
                    "message": "Quota exceeded for quota metric 'Read requests' and limit 'Read requests per day'",
                    "status": "RESOURCE_EXHAUSTED",
                }
            },
        )
    )

    with pytest.raises(QuotaExceededException) as exc_info:
        read(name, resource_id)

    assert "Quota exceeded while trying to read" in str(exc_info.value)
    assert resource_id in str(exc_info.value)


@respx.mock
def test_read_403_permission_denied(mock_session):
    """Test that read() raises WalletException with proper message when access is denied."""
    name = "GenericObject"
    resource_id = "test.resource.id"
    url = client_pool.url(name, f"/{resource_id}")

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
        read(name, resource_id)

    # Should NOT be QuotaExceededException
    assert not isinstance(exc_info.value, QuotaExceededException)
    assert "Access denied while trying to read" in str(exc_info.value)
    assert resource_id in str(exc_info.value)


@respx.mock
def test_create_403_quota_exceeded(mock_session):
    """Test that create() raises QuotaExceededException when quota is exceeded."""
    name = "GenericClass"
    data = new(
        name,
        {
            "id": "test.class.id",
            "enableSmartTap": False,
            "multipleDevicesAndHoldersAllowedStatus": enums.MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED,
            "viewUnlockRequirement": enums.ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED,
        },
    )
    url = client_pool.url(name)

    # Mock a 403 response with quota error message
    respx.post(url).mock(
        return_value=httpx.Response(
            403,
            json={
                "error": {
                    "code": 403,
                    "message": "Quota exceeded for quota metric 'Write requests'",
                    "status": "RESOURCE_EXHAUSTED",
                }
            },
        )
    )

    with pytest.raises(QuotaExceededException) as exc_info:
        create(data)

    assert "Quota exceeded while trying to create" in str(exc_info.value)


@respx.mock
def test_create_403_permission_denied(mock_session):
    """Test that create() raises WalletException when access is denied."""
    name = "GenericClass"
    data = new(
        name,
        {
            "id": "test.class.id",
            "enableSmartTap": False,
            "multipleDevicesAndHoldersAllowedStatus": enums.MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED,
            "viewUnlockRequirement": enums.ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED,
        },
    )
    url = client_pool.url(name)

    # Mock a 403 response with permission denied message
    respx.post(url).mock(
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
        create(data)

    assert not isinstance(exc_info.value, QuotaExceededException)
    assert "Access denied while trying to create" in str(exc_info.value)


@respx.mock
def test_update_403_quota_exceeded(mock_session):
    """Test that update() raises QuotaExceededException when quota is exceeded."""
    name = "GenericClass"
    data = new(
        name,
        {
            "id": "test.class.id",
            "enableSmartTap": True,
            "multipleDevicesAndHoldersAllowedStatus": enums.MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED,
            "viewUnlockRequirement": enums.ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED,
        },
    )
    url = client_pool.url(name, "/test.class.id")

    # Mock a 403 response with rate limit error message
    respx.patch(url).mock(
        return_value=httpx.Response(
            403,
            json={
                "error": {
                    "code": 403,
                    "message": "Rate limit exceeded",
                    "status": "RESOURCE_EXHAUSTED",
                }
            },
        )
    )

    with pytest.raises(QuotaExceededException) as exc_info:
        update(data)

    assert "Quota exceeded while trying to update" in str(exc_info.value)


@respx.mock
def test_update_403_permission_denied(mock_session):
    """Test that update() raises WalletException when access is denied."""
    name = "GenericClass"
    data = new(
        name,
        {
            "id": "test.class.id",
            "enableSmartTap": True,
            "multipleDevicesAndHoldersAllowedStatus": enums.MultipleDevicesAndHoldersAllowedStatus.STATUS_UNSPECIFIED,
            "viewUnlockRequirement": enums.ViewUnlockRequirement.VIEW_UNLOCK_REQUIREMENT_UNSPECIFIED,
        },
    )
    url = client_pool.url(name, "/test.class.id")

    # Mock a 403 response with permission denied message
    respx.patch(url).mock(
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
        update(data)

    assert not isinstance(exc_info.value, QuotaExceededException)
    assert "Access denied while trying to update" in str(exc_info.value)


@respx.mock
def test_message_403_quota_exceeded(mock_session):
    """Test that message() raises QuotaExceededException when quota is exceeded."""
    name = "GenericObject"
    resource_id = "test.object.id"
    msg = {"header": "Test", "body": "Test message"}
    url = client_pool.url(name, f"/{resource_id}/addMessage")

    # Mock a 403 response with quota error message
    respx.post(url).mock(
        return_value=httpx.Response(
            403,
            json={
                "error": {
                    "code": 403,
                    "message": "Quota exceeded",
                    "status": "RESOURCE_EXHAUSTED",
                }
            },
        )
    )

    with pytest.raises(QuotaExceededException) as exc_info:
        message(name, resource_id, msg)

    assert "Quota exceeded while trying to send message" in str(exc_info.value)


@respx.mock
def test_message_403_permission_denied(mock_session):
    """Test that message() raises WalletException when access is denied."""
    name = "GenericObject"
    resource_id = "test.object.id"
    msg = {"header": "Test", "body": "Test message"}
    url = client_pool.url(name, f"/{resource_id}/addMessage")

    # Mock a 403 response with permission denied message
    respx.post(url).mock(
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
        message(name, resource_id, msg)

    assert not isinstance(exc_info.value, QuotaExceededException)
    assert "Access denied while trying to send message" in str(exc_info.value)
