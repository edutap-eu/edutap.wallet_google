"""Tests for building and executing a Batch."""

from edutap.wallet_google.batch import Batch
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


def _mock_batch_endpoint():
    """Point the batch endpoint at a canned two-part response."""
    return respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=MULTIPART_RESPONSE.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )


def test_len_counts_the_added_sub_requests():
    """A Batch is one HTTP request; len() is how the caller sees its size."""
    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.one", "state": "EXPIRED"})
    batch.add_update("LoyaltyObject", {"id": "issuer.two", "state": "ACTIVE"})

    assert len(batch) == 2


@respx.mock
def test_execute_sends_one_request_and_returns_one_result_per_item(mock_session):
    """Two updates go out as a single POST and come back as two results."""
    route = _mock_batch_endpoint()

    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.one", "state": "EXPIRED"})
    batch.add_update("GenericObject", {"id": "issuer.two", "state": "ACTIVE"})
    results = batch.execute()

    assert route.call_count == 1
    assert len(results) == 2
    assert results[0].ok is True
    assert results[0].resource_id == "issuer.one"
    assert results[0].body is not None
    assert results[0].body["state"] == "EXPIRED"
    assert results[1].ok is False
    assert results[1].error.code == 404
    assert results[1].error.message == "not found"


@respx.mock
def test_a_batch_may_mix_pass_types(mock_session):
    """Each part carries its own path, so types need not match."""
    route = _mock_batch_endpoint()

    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.one", "state": "EXPIRED"})
    batch.add_update("EventTicketObject", {"id": "issuer.two", "state": "ACTIVE"})
    results = batch.execute()

    body = route.calls.last.request.content.decode("utf-8")
    assert "PATCH /walletobjects/v1/genericObject/issuer.one" in body
    assert "PATCH /walletobjects/v1/eventTicketObject/issuer.two" in body
    assert [r.name for r in results] == ["GenericObject", "EventTicketObject"]


@respx.mock
def test_execute_sends_only_the_attributes_that_were_set(mock_session):
    """A two-attribute PATCH must not carry the rest of the model."""
    route = _mock_batch_endpoint()

    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.one", "state": "EXPIRED"})
    batch.execute()

    body = route.calls.last.request.content.decode("utf-8")
    assert '"state"' in body
    assert '"classId"' not in body


def test_add_updates_appends_a_whole_list():
    """The bulk case must not need one call per object."""
    batch = Batch()
    batch.add_updates(
        "LoyaltyObject",
        [{"id": f"issuer.{n}", "state": "EXPIRED"} for n in range(5)],
    )

    assert len(batch) == 5


def test_add_update_rejects_an_unknown_attribute():
    """Typos fail on the line that caused them, not at execute() time."""
    batch = Batch()

    with pytest.raises(ValueError) as exc_info:
        batch.add_update("GenericObject", {"id": "issuer.one", "notAField": 1})

    assert "notAField" in str(exc_info.value)


def test_add_update_requires_the_resource_id():
    """Without an id there is nothing to PATCH."""
    batch = Batch()

    with pytest.raises(ValueError) as exc_info:
        batch.add_update("GenericObject", {"state": "EXPIRED"})

    assert "id" in str(exc_info.value)


def test_executing_an_empty_batch_makes_no_request():
    """Nothing added, nothing sent."""
    batch = Batch()

    assert batch.execute() == []


@respx.mock
def test_sub_requests_are_grouped_by_pass_type_on_the_wire(mock_session):
    """Batch may reorder internally; interleaved types come out grouped."""
    route = _mock_batch_endpoint()

    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.g1", "state": "EXPIRED"})
    batch.add_update("LoyaltyObject", {"id": "issuer.l1", "state": "EXPIRED"})
    batch.add_update("GenericObject", {"id": "issuer.g2", "state": "EXPIRED"})
    batch.execute()

    body = route.calls.last.request.content.decode("utf-8")
    positions = [
        body.index("genericObject/issuer.g1"),
        body.index("genericObject/issuer.g2"),
        body.index("loyaltyObject/issuer.l1"),
    ]
    assert positions == sorted(positions), "the two genericObjects should be adjacent"


@respx.mock
def test_results_follow_add_order_even_when_the_server_shuffles(mock_session):
    """The invariant: add order is result order, whatever happens in between.

    The canned response deliberately returns item-1 before item-0, which is what
    correlation by Content-ID is for.
    """
    shuffled = (
        "--rspboundary\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: <response-item-1>\r\n"
        "\r\n"
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"id": "issuer.two"}\r\n'
        "\r\n"
        "--rspboundary\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: <response-item-0>\r\n"
        "\r\n"
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"id": "issuer.one"}\r\n'
        "\r\n"
        "--rspboundary--\r\n"
    )
    respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=shuffled.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )

    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.one", "state": "EXPIRED"})
    batch.add_update("LoyaltyObject", {"id": "issuer.two", "state": "EXPIRED"})
    results = batch.execute()

    assert [r.resource_id for r in results] == ["issuer.one", "issuer.two"]
    assert [r.index for r in results] == [0, 1]
    assert results[0].body is not None
    assert results[1].body is not None
    assert results[0].body["id"] == "issuer.one"
    assert results[1].body["id"] == "issuer.two"


@pytest.mark.parametrize(
    "name,url_part",
    [
        ("GenericObject", "genericObject"),
        ("LoyaltyObject", "loyaltyObject"),
        ("OfferObject", "offerObject"),
        ("GiftCardObject", "giftCardObject"),
        ("EventTicketObject", "eventTicketObject"),
        ("TransitObject", "transitObject"),
        ("FlightObject", "flightObject"),
    ],
)
@respx.mock
def test_batch_builds_the_right_path_for_every_pass_type(mock_session, name, url_part):
    """The sub-request path comes from the registry, so every type works."""
    route = _mock_batch_endpoint()

    batch = Batch()
    batch.add_update(name, {"id": "issuer.one", "state": "EXPIRED"})
    batch.execute()

    body = route.calls.last.request.content.decode("utf-8")
    assert f"PATCH /walletobjects/v1/{url_part}/issuer.one" in body
