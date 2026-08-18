"""Tests for multipart/mixed encoding and decoding."""

from edutap.wallet_google.multipart import _PART_CONTENT_TYPE
from edutap.wallet_google.multipart import decode_multipart
from edutap.wallet_google.multipart import encode_multipart
from edutap.wallet_google.multipart import SubRequest


def test_encode_produces_one_part_per_sub_request():
    """Each sub-request becomes a delimited part carrying method, path and body."""
    sub_requests = [
        SubRequest(
            method="PATCH",
            path="/walletobjects/v1/genericObject/issuer.one",
            body='{"state":"EXPIRED"}',
            content_id="item-0",
        ),
        SubRequest(
            method="PATCH",
            path="/walletobjects/v1/loyaltyObject/issuer.two",
            body='{"state":"ACTIVE"}',
            content_id="item-1",
        ),
    ]

    encoded = encode_multipart(sub_requests, boundary="testboundary").decode("utf-8")

    assert encoded.count("--testboundary\r\n") == 2
    assert encoded.endswith("--testboundary--\r\n")
    assert "Content-ID: <item-0>" in encoded
    assert "Content-ID: <item-1>" in encoded
    assert "PATCH /walletobjects/v1/genericObject/issuer.one" in encoded
    assert "PATCH /walletobjects/v1/loyaltyObject/issuer.two" in encoded
    assert '{"state":"EXPIRED"}' in encoded


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


def test_decode_returns_one_sub_response_per_part():
    """Status code, body and Content-ID are recovered from each part."""
    responses = decode_multipart(
        MULTIPART_RESPONSE.encode("utf-8"),
        "multipart/mixed; boundary=rspboundary",
    )

    assert len(responses) == 2
    assert responses[0].status_code == 200
    assert responses[0].body == {"id": "issuer.one", "state": "EXPIRED"}
    assert responses[1].status_code == 404
    assert responses[1].body is not None
    assert responses[1].body["error"]["code"] == 404


def test_decode_strips_the_response_prefix_from_content_id():
    """Google echoes Content-ID with a 'response-' prefix; we map back to ours."""
    responses = decode_multipart(
        MULTIPART_RESPONSE.encode("utf-8"),
        "multipart/mixed; boundary=rspboundary",
    )

    assert [r.content_id for r in responses] == ["item-0", "item-1"]


MALFORMED_STATUS_LINE_RESPONSE = (
    "--rspboundary\r\n"
    "Content-Type: application/http\r\n"
    "Content-ID: <response-item-0>\r\n"
    "\r\n"
    "not a valid status line\r\n"
    "Content-Type: application/json\r\n"
    "\r\n"
    '{"id": "issuer.one"}\r\n'
    "\r\n"
    "--rspboundary--\r\n"
)


def test_decode_returns_status_code_zero_for_malformed_status_line():
    """A part with a malformed status line must not crash the whole decode.

    One malformed part in a batch of hundreds must degrade to a result,
    not blow up the entire ``decode_multipart`` call.
    """
    responses = decode_multipart(
        MALFORMED_STATUS_LINE_RESPONSE.encode("utf-8"),
        "multipart/mixed; boundary=rspboundary",
    )

    assert len(responses) == 1
    assert responses[0].status_code == 0


NON_DICT_JSON_BODY_RESPONSE = (
    "--rspboundary\r\n"
    "Content-Type: application/http\r\n"
    "Content-ID: <response-item-0>\r\n"
    "\r\n"
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: application/json\r\n"
    "\r\n"
    "[1, 2, 3]\r\n"
    "\r\n"
    "--rspboundary--\r\n"
)


def test_decode_degrades_a_non_dict_json_body_to_none():
    """json.loads() may return a list or scalar. SubResponse.body is typed
    ``dict | None``; a list must degrade to None rather than being carried
    through and later exploding a strict pydantic model with a shape it never
    declared.
    """
    responses = decode_multipart(
        NON_DICT_JSON_BODY_RESPONSE.encode("utf-8"),
        "multipart/mixed; boundary=rspboundary",
    )

    assert len(responses) == 1
    assert responses[0].status_code == 200
    assert responses[0].body is None


def test_encode_rejects_a_path_with_a_bare_cr_or_lf():
    """A CR or LF inside a resource id would inject lines into the part and shift
    the body -- api.update() cannot do this because httpx rejects it, but
    add_update() builds the path itself with no equivalent guard.
    """
    sub_requests = [
        SubRequest(
            method="PATCH",
            path="/walletobjects/v1/genericObject/issuer.one\r\nEvil-Header: x",
            body='{"state":"EXPIRED"}',
            content_id="item-0",
        )
    ]

    try:
        encode_multipart(sub_requests, boundary="testboundary")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for a path containing CRLF")


def test_encode_rejects_a_content_id_with_a_bare_lf():
    """Same injection risk via content_id."""
    sub_requests = [
        SubRequest(
            method="PATCH",
            path="/walletobjects/v1/genericObject/issuer.one",
            body='{"state":"EXPIRED"}',
            content_id="item-0\nContent-Type: text/evil",
        )
    ]

    try:
        encode_multipart(sub_requests, boundary="testboundary")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for a content_id containing LF")


def test_encode_rejects_a_method_with_a_bare_cr():
    """Same injection risk via method, for completeness."""
    sub_requests = [
        SubRequest(
            method="PATCH\rEvil: x",
            path="/walletobjects/v1/genericObject/issuer.one",
            body='{"state":"EXPIRED"}',
            content_id="item-0",
        )
    ]

    try:
        encode_multipart(sub_requests, boundary="testboundary")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for a method containing CR")


LF_ONLY_RESPONSE = (
    "--rspboundary\r\n"
    "Content-Type: application/http\r\n"
    "Content-ID: <response-item-0>\r\n"
    "\r\n"
    "HTTP/1.1 200 OK\n"
    "Content-Type: application/json\n"
    "\n"
    '{"id": "issuer.one"}\r\n'
    "\r\n"
    "--rspboundary--\r\n"
)


def test_decode_finds_the_body_when_the_part_uses_lf_only_headers():
    """_parse_http_payload splits on CRLFCRLF; an LF-only sub-response must still
    surface its body rather than silently losing it (ok=True, body=None, no error).
    """
    responses = decode_multipart(
        LF_ONLY_RESPONSE.encode("utf-8"),
        "multipart/mixed; boundary=rspboundary",
    )

    assert len(responses) == 1
    assert responses[0].status_code == 200
    assert responses[0].body == {"id": "issuer.one"}


def test_part_content_type_is_pinned_to_application_json():
    """_PART_CONTENT_TYPE's whole purpose is that flipping it to application/http is
    a deliberate, larger change (it also needs an HTTP-version suffix on the request
    line and a per-part Content-Type header). Pin the current value so a bare flip
    announces itself as a broken test rather than passing silently.
    """
    assert _PART_CONTENT_TYPE == "application/json"
