"""Tests for multipart/mixed encoding and decoding."""

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
