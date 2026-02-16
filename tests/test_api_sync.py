"""Comprehensive tests for synchronous API CRUD operations (beyond basic create tests)."""

import httpx
import pytest
import respx

from edutap.wallet_google.api import listing, message, new, read, update
from edutap.wallet_google.clientpool import client_pool
from edutap.wallet_google.models.datatypes import enums


@respx.mock
def test_read_generic_class(mock_session):
    """Test reading a GenericClass."""
    name = "GenericClass"
    class_id = "test.class.123"
    url = client_pool.url(name, f"/{class_id}")

    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": class_id,
                "enableSmartTap": True,
            },
        )
    )

    result = read(name, class_id)

    assert result.id == class_id
    assert result.enableSmartTap is True


@respx.mock
def test_read_generic_object(mock_session):
    """Test reading a GenericObject."""
    name = "GenericObject"
    object_id = "test.object.123"
    url = client_pool.url(name, f"/{object_id}")

    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": object_id,
                "classId": "test.class.123",
                "state": "ACTIVE",
            },
        )
    )

    result = read(name, object_id)

    assert result.id == object_id
    assert result.state == enums.State.ACTIVE


@respx.mock
def test_read_404_not_found(mock_session):
    """Test that read raises LookupError on 404."""
    name = "GenericClass"
    class_id = "test.class.nonexistent"
    url = client_pool.url(name, f"/{class_id}")

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
        read(name, class_id)

    assert "not found" in str(exc_info.value)


@respx.mock
def test_update_generic_object_partial(mock_session):
    """Test partial update of a GenericObject."""
    name = "GenericObject"
    object_id = "test.object.123"
    url = client_pool.url(name, f"/{object_id}")

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

    data = new(
        name,
        {
            "id": object_id,
            "classId": "test.class.123",
            "state": enums.State.EXPIRED,
        },
    )
    result = update(data, partial=True)

    assert result.id == object_id
    assert result.state == enums.State.EXPIRED


@respx.mock
def test_update_generic_object_full(mock_session):
    """Test full update of a GenericObject."""
    name = "GenericObject"
    object_id = "test.object.123"
    url = client_pool.url(name, f"/{object_id}")

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

    data = new(
        name,
        {
            "id": object_id,
            "classId": "test.class.123",
            "state": enums.State.INACTIVE,
        },
    )
    result = update(data, partial=False)

    assert result.id == object_id
    assert result.state == enums.State.INACTIVE


@respx.mock
def test_update_404_not_found(mock_session):
    """Test that update raises LookupError on 404."""
    name = "GenericObject"
    object_id = "test.object.nonexistent"
    url = client_pool.url(name, f"/{object_id}")

    respx.patch(url).mock(
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

    data = new(name, {"id": object_id, "classId": "test.class.123", "state": "ACTIVE"})

    with pytest.raises(LookupError) as exc_info:
        update(data)

    assert "not found" in str(exc_info.value)


@respx.mock
def test_message_generic_object(mock_session):
    """Test sending a message to a GenericObject."""
    name = "GenericObject"
    object_id = "test.object.123"
    url = client_pool.url(name, f"/{object_id}/addMessage")

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

    result = message(
        name,
        object_id,
        {
            "header": "Test Header",
            "body": "Test message body",
        },
    )

    assert result.id == object_id


@respx.mock
def test_listing_generic_classes(mock_session):
    """Test listing GenericClasses."""
    name = "GenericClass"
    issuer_id = "1234567890"
    url = client_pool.url(name)

    respx.get(url).mock(
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

    results = list(listing(name, issuer_id=issuer_id))

    assert len(results) == 2
    assert results[0].id == f"{issuer_id}.class1"
    assert results[1].id == f"{issuer_id}.class2"


@respx.mock
def test_listing_generic_objects(mock_session):
    """Test listing GenericObjects for a class."""
    name = "GenericObject"
    class_id = "test.class.123"
    url = client_pool.url(name)

    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "resources": [
                    {"id": "obj1", "classId": class_id},
                    {"id": "obj2", "classId": class_id},
                ]
            },
        )
    )

    results = list(listing(name, resource_id=class_id))

    assert len(results) == 2
    assert results[0].id == "obj1"
    assert results[1].id == "obj2"


@respx.mock
def test_listing_empty_result(mock_session):
    """Test listing with empty results."""
    name = "GenericObject"
    class_id = "test.class.empty"
    url = client_pool.url(name)

    respx.get(url).mock(return_value=httpx.Response(200, json={"resources": []}))

    results = list(listing(name, resource_id=class_id))

    assert len(results) == 0


@respx.mock
def test_listing_with_pagination_token(mock_session):
    """Test listing returns pagination token when result_per_page is set."""
    name = "GenericObject"
    class_id = "test.class.123"
    url = client_pool.url(name)

    # The API will add params: classId and maxResults
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "resources": [
                    {"id": "obj1", "classId": class_id, "state": "ACTIVE"},
                    {"id": "obj2", "classId": class_id, "state": "ACTIVE"},
                ],
                "pagination": {"nextPageToken": "token123", "resultsPerPage": 2},
            },
        )
    )

    results = list(listing(name, resource_id=class_id, result_per_page=2))

    # Should have 2 objects + 1 token string
    assert len(results) == 3
    assert results[0].id == "obj1"
    assert results[1].id == "obj2"
    assert isinstance(results[2], str)
    assert results[2] == "token123"


@respx.mock
def test_listing_auto_pagination(mock_session):
    """Test listing automatically fetches all pages when result_per_page not set."""
    name = "GenericObject"
    class_id = "test.class.123"
    url = client_pool.url(name)

    # First request - with pagination token
    # Second request - without pagination token (last page)
    respx.get(url).mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "resources": [
                        {"id": "obj1", "classId": class_id, "state": "ACTIVE"},
                        {"id": "obj2", "classId": class_id, "state": "ACTIVE"},
                    ],
                    "pagination": {"nextPageToken": "token123", "resultsPerPage": 2},
                },
            ),
            httpx.Response(
                200,
                json={
                    "resources": [
                        {"id": "obj3", "classId": class_id, "state": "ACTIVE"},
                    ],
                    "pagination": {"resultsPerPage": 1},
                },
            ),
        ]
    )

    results = list(listing(name, resource_id=class_id))

    # Should have all 3 objects, no token
    assert len(results) == 3
    assert all(not isinstance(r, str) for r in results)
    assert results[0].id == "obj1"
    assert results[1].id == "obj2"
    assert results[2].id == "obj3"


@respx.mock
def test_listing_validation_error_resource_and_issuer():
    """Test that listing raises ValueError when both resource_id and issuer_id are provided."""
    with pytest.raises(ValueError) as exc_info:
        list(listing("GenericClass", resource_id="test", issuer_id="issuer"))

    assert "mutually exclusive" in str(exc_info.value)


@respx.mock
def test_listing_validation_error_missing_resource_id():
    """Test that listing raises ValueError when resource_id is missing for objects."""
    with pytest.raises(ValueError) as exc_info:
        list(listing("GenericObject"))

    assert "resource_id" in str(exc_info.value)


@respx.mock
def test_listing_validation_error_missing_issuer_id():
    """Test that listing raises ValueError when issuer_id is missing for classes."""
    with pytest.raises(ValueError) as exc_info:
        list(listing("GenericClass"))

    assert "issuer_id" in str(exc_info.value)
