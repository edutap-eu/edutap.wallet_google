"""Tests for Batch.aexecute()."""

from edutap.wallet_google.batch import Batch
from edutap.wallet_google.exceptions import QuotaExceededException
from edutap.wallet_google.settings import Settings

import httpx
import pytest
import respx


MULTIPART_RESPONSE = (
    "--rspboundary\r\n"
    "Content-Type: application/http\r\n"
    "Content-ID: <response-item-0>\r\n"
    "\r\n"
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: application/json\r\n"
    "\r\n"
    '{"id": "issuer.one", "state": "EXPIRED"}\r\n'
    "\r\n"
    "--rspboundary\r\n"
    "Content-Type: application/http\r\n"
    "Content-ID: <response-item-1>\r\n"
    "\r\n"
    "HTTP/1.1 404 Not Found\r\n"
    "Content-Type: application/json\r\n"
    "\r\n"
    '{"error": {"code": 404, "message": "not found", "status": "NOT_FOUND"}}\r\n'
    "\r\n"
    "--rspboundary--\r\n"
)


@pytest.mark.asyncio
@respx.mock
async def test_aexecute_matches_the_sync_behaviour(mock_async_session):
    """One POST, one result per item, failures reported not raised."""
    route = respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=MULTIPART_RESPONSE.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )

    batch = Batch()
    batch.add_update("LoyaltyObject", {"id": "issuer.one", "state": "EXPIRED"})
    batch.add_update("LoyaltyObject", {"id": "issuer.two", "state": "ACTIVE"})
    results = await batch.aexecute()

    assert route.call_count == 1
    assert len(results) == 2
    assert results[0].ok is True
    assert results[1].ok is False
    assert results[1].error.code == 404


@pytest.mark.asyncio
async def test_aexecute_on_an_empty_batch_makes_no_request(mock_async_session):
    """Nothing added, nothing sent."""
    assert await Batch().aexecute() == []


@pytest.mark.asyncio
@respx.mock
async def test_aexecute_batch_post_failure_raises_instead_of_returning_results(
    mock_async_session,
):
    """A 403 quota response to the batch POST itself must raise, not be handed to
    decode_multipart as if it were a multipart body.
    """
    respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            403,
            json={
                "error": {
                    "code": 403,
                    "message": (
                        "Quota exceeded for quota metric 'Write requests' and "
                        "limit 'Write requests per day'"
                    ),
                    "status": "RESOURCE_EXHAUSTED",
                }
            },
        )
    )

    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.one", "state": "EXPIRED"})

    with pytest.raises(QuotaExceededException):
        await batch.aexecute()
