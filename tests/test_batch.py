"""Tests for building and executing a Batch."""

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


@respx.mock
def test_result_has_an_error_when_the_server_returns_non_2xx_without_an_error_body(
    mock_session,
):
    """ok is False must never leave error as None; callers read error.message."""
    no_error_body = (
        "--rspboundary\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: <response-item-0>\r\n"
        "\r\n"
        "HTTP/1.1 500 Internal Server Error\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"unexpected": "shape"}\r\n'
        "\r\n"
        "--rspboundary--\r\n"
    )
    respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=no_error_body.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )

    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.one", "state": "EXPIRED"})
    results = batch.execute()

    assert results[0].ok is False
    assert results[0].error is not None
    assert results[0].error.message  # must not raise, must not be empty


@respx.mock
def test_result_has_an_error_when_the_status_line_could_not_be_parsed(mock_session):
    """A malformed status line degrades to status_code=0, not to error=None."""
    malformed_status_line = (
        "--rspboundary\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: <response-item-0>\r\n"
        "\r\n"
        "GARBAGE NOT A STATUS LINE\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        "\r\n"
        "--rspboundary--\r\n"
    )
    respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=malformed_status_line.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )

    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.one", "state": "EXPIRED"})
    results = batch.execute()

    assert results[0].status_code == 0
    assert results[0].ok is False
    assert results[0].error is not None
    assert results[0].error.message  # must not raise, must not be empty


@respx.mock
def test_a_normally_shaped_google_error_does_not_destroy_the_whole_batch(mock_session):
    """A real Google error body carries `details` (and sometimes `errors`); it must not
    make BatchError.model_validate() raise and discard every result in the batch,
    including the successful ones sitting right next to it.
    """
    realistic_error_and_a_success = (
        "--rspboundary\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: <response-item-0>\r\n"
        "\r\n"
        "HTTP/1.1 400 Bad Request\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"error": {"code": 400, "message": "bad", "status": "INVALID_ARGUMENT", '
        '"details": [{"@type": "type.googleapis.com/google.rpc.BadRequest"}], '
        '"errors": [{"message": "bad", "domain": "global", "reason": "invalid"}]}}\r\n'
        "\r\n"
        "--rspboundary\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: <response-item-1>\r\n"
        "\r\n"
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"id": "issuer.two", "state": "EXPIRED"}\r\n'
        "\r\n"
        "--rspboundary--\r\n"
    )
    respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=realistic_error_and_a_success.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )

    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.one", "state": "EXPIRED"})
    batch.add_update("GenericObject", {"id": "issuer.two", "state": "EXPIRED"})
    results = batch.execute()

    assert results[0].ok is False
    assert results[0].error is not None
    assert results[0].error.code == 400
    assert results[0].error.message == "bad"
    # The point: a realistically-shaped error must not take the successful
    # sub-request down with it.
    assert results[1].ok is True
    assert results[1].body is not None
    assert results[1].body["id"] == "issuer.two"


@respx.mock
def test_batch_post_failure_raises_instead_of_returning_results(mock_session):
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
        batch.execute()


@respx.mock
def test_results_correlate_correctly_when_wire_order_differs_from_add_order(
    mock_session,
):
    """Reordering (grouping by pass type) and correlation must work together: each
    result's body must match its own resource_id, not the one that happened to land
    in the same wire position.
    """
    batch = Batch()
    # Add order: Loyalty, Generic, Loyalty -- wire order groups by type, so this
    # differs from add order for at least one item.
    batch.add_update("LoyaltyObject", {"id": "issuer.l1", "state": "EXPIRED"})
    batch.add_update("GenericObject", {"id": "issuer.g1", "state": "ACTIVE"})
    batch.add_update("LoyaltyObject", {"id": "issuer.l2", "state": "EXPIRED"})

    body = None

    def _respond(request: httpx.Request) -> httpx.Response:
        nonlocal body
        body = request.content.decode("utf-8")
        # Build a response whose Content-IDs correlate by content, not by wire
        # position, and whose part order does not match request part order either.
        parts = []
        for content_id, resource_id in [
            ("item-2", "issuer.l2"),
            ("item-0", "issuer.l1"),
            ("item-1", "issuer.g1"),
        ]:
            parts.append(
                "--rspboundary\r\n"
                "Content-Type: application/http\r\n"
                f"Content-ID: <response-{content_id}>\r\n"
                "\r\n"
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "\r\n"
                f'{{"id": "{resource_id}"}}\r\n'
                "\r\n"
            )
        parts.append("--rspboundary--\r\n")
        return httpx.Response(
            200,
            content="".join(parts).encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )

    respx.post(str(Settings().batch_url)).mock(side_effect=_respond)

    results = batch.execute()

    assert [r.resource_id for r in results] == ["issuer.l1", "issuer.g1", "issuer.l2"]
    for result in results:
        assert result.body is not None
        assert result.body["id"] == result.resource_id


@respx.mock
def test_execute_sends_matching_content_type_header_and_boundary(mock_session):
    """The Content-Type header must announce multipart/mixed with a boundary that
    matches the one actually used in the body -- a mismatch here would leave the
    suite green while making every real request fail.
    """
    _mock_batch_endpoint()

    batch = Batch()
    batch.add_update("GenericObject", {"id": "issuer.one", "state": "EXPIRED"})
    batch.execute()

    request = respx.calls.last.request
    content_type = request.headers["Content-Type"]
    assert content_type.startswith("multipart/mixed; boundary=")
    boundary = content_type.split("boundary=", 1)[1]
    body = request.content.decode("utf-8")
    assert f"--{boundary}" in body


@respx.mock
def test_add_create_posts_to_the_collection_path(mock_session):
    """Create is a POST to the type's collection, with no id in the path."""
    route = _mock_batch_endpoint()

    batch = Batch()
    batch.add_create(
        "GenericObject",
        {"id": "issuer.new-one", "classId": "issuer.class", "state": "ACTIVE"},
    )
    batch.execute()

    body = route.calls.last.request.content.decode("utf-8")
    assert "POST /walletobjects/v1/genericObject" in body
    # the id belongs in the payload, not the path
    assert "POST /walletobjects/v1/genericObject/issuer.new-one" not in body
    assert '"id":"issuer.new-one"' in body.replace(" ", "")


def test_add_create_requires_the_models_required_fields():
    """Unlike add_update, create does not relax required fields."""
    batch = Batch()

    with pytest.raises(ValueError) as exc_info:
        batch.add_create("GenericObject", {"id": "issuer.new-one"})

    assert "classId" in str(exc_info.value)


@respx.mock
def test_a_batch_may_mix_creates_and_updates(mock_session):
    """Method is per sub-request, so both fit in one batch."""
    route = _mock_batch_endpoint()

    batch = Batch()
    batch.add_create(
        "GenericObject",
        {"id": "issuer.new-one", "classId": "issuer.class", "state": "ACTIVE"},
    )
    batch.add_update("GenericObject", {"id": "issuer.old-one", "state": "EXPIRED"})
    batch.execute()

    body = route.calls.last.request.content.decode("utf-8")
    assert "POST /walletobjects/v1/genericObject" in body
    assert "PATCH /walletobjects/v1/genericObject/issuer.old-one" in body


def test_add_creates_appends_a_whole_list():
    """The bulk case must not need one call per object."""
    batch = Batch()
    batch.add_creates(
        "GenericObject",
        [
            {"id": f"issuer.{n}", "classId": "issuer.class", "state": "ACTIVE"}
            for n in range(5)
        ],
    )

    assert len(batch) == 5


@respx.mock
def test_an_already_existing_object_comes_back_as_a_result(mock_session):
    """409 is the common create failure and must not raise."""
    conflict = (
        "--rspboundary\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: <response-item-0>\r\n"
        "\r\n"
        "HTTP/1.1 409 Conflict\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"error": {"code": 409, "message": "already exists", '
        '"status": "ALREADY_EXISTS"}}\r\n'
        "\r\n"
        "--rspboundary--\r\n"
    )
    respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=conflict.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )

    batch = Batch()
    batch.add_create(
        "GenericObject",
        {"id": "issuer.new-one", "classId": "issuer.class", "state": "ACTIVE"},
    )
    results = batch.execute()

    assert results[0].ok is False
    assert results[0].error is not None
    assert results[0].error.code == 409
