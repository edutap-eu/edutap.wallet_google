"""Encoding and decoding of ``multipart/mixed`` bodies.

This module deliberately knows nothing about wallet models, settings or HTTP
clients. It turns sub-requests into bytes and bytes back into sub-responses,
which makes the fiddly format details testable without a network.

See https://developers.google.com/wallet/generic/resources/performance-tips
"""

from dataclasses import dataclass
from email.parser import BytesParser
from email.policy import HTTP

import json
import re
import uuid


# Google's Wallet examples show the parts as application/json. Google's general
# batch protocol uses application/http. The Wallet documentation is what we have,
# so follow it — and keep it in one place so it is a one-line change if the
# server turns out to want the other one.
_PART_CONTENT_TYPE = "application/json"

# multipart requires CRLF line endings (RFC 2046).
_CRLF = "\r\n"


@dataclass
class SubRequest:
    """A single HTTP request to be carried inside a multipart body."""

    method: str
    path: str
    body: str | None
    content_id: str


@dataclass
class SubResponse:
    """A single HTTP response extracted from a multipart body."""

    content_id: str | None
    status_code: int
    body: dict | None


def make_boundary() -> str:
    """Return a boundary that cannot collide with the payload."""
    return f"batch_{uuid.uuid4().hex}"


def _reject_crlf(value: str, field: str) -> None:
    """Raise if *value* contains a bare CR or LF.

    A resource id (or, in principle, a method) is interpolated straight into the
    request line. Nothing upstream constrains it: ``api.update()`` cannot carry a
    CR/LF because httpx rejects it in the URL, but ``Batch.add_update()`` builds the
    path itself with no equivalent guard. Left unchecked, a CR or LF injects extra
    lines into the part and shifts the body -- surfacing later as an opaque error
    from Google instead of a clear one from here.

    :param value: The value to check.
    :param field: Name of the field, for the error message.
    :raises ValueError: When *value* contains ``\\r`` or ``\\n``.
    """
    if "\r" in value or "\n" in value:
        raise ValueError(f"{field} must not contain CR or LF: {value!r}")


def encode_multipart(sub_requests: list[SubRequest], boundary: str) -> bytes:
    """Encode sub-requests as a ``multipart/mixed`` body.

    :param sub_requests: The requests to carry, in order.
    :param boundary:     Delimiter between the parts, without leading dashes.
    :raises ValueError:  When a sub-request's ``path``, ``method`` or ``content_id``
                          contains a CR or LF, which would corrupt the framing.
    :return:             The encoded body, ready to be sent as request content.
    """
    lines: list[str] = []
    for sub_request in sub_requests:
        _reject_crlf(sub_request.path, "path")
        _reject_crlf(sub_request.method, "method")
        _reject_crlf(sub_request.content_id, "content_id")
        lines.append(f"--{boundary}")
        lines.append(f"Content-Type: {_PART_CONTENT_TYPE}")
        lines.append(f"Content-ID: <{sub_request.content_id}>")
        lines.append("")
        lines.append(f"{sub_request.method} {sub_request.path}")
        if sub_request.body is not None:
            lines.append("")
            lines.append(sub_request.body)
        lines.append("")
    lines.append(f"--{boundary}--")
    lines.append("")
    return _CRLF.join(lines).encode("utf-8")


def _parse_http_payload(payload: str) -> tuple[int, dict | None]:
    """Parse an embedded HTTP response into status code and JSON body.

    :param payload: A raw HTTP response: status line, headers, blank line, body.
    :return:        Tuple of status code and decoded body (None when not JSON).
    """
    # Split on the blank line between headers and body. RFC 2046 requires CRLF,
    # but tolerate a bare LF too: an LF-only sub-response must still surface its
    # body rather than silently losing it.
    head, *rest = re.split(r"\r?\n\r?\n", payload, maxsplit=1)
    body = rest[0] if rest else ""
    status_line = re.split(r"\r?\n", head, maxsplit=1)[0]
    try:
        # "HTTP/1.1 404 Not Found" -> 404
        status_code = int(status_line.split(" ")[1])
    except (IndexError, ValueError):
        # A single malformed part must not crash the whole batch decode: 0 is
        # never a real HTTP status, and callers already treat any non-2xx
        # status as not-ok, so this degrades gracefully into the existing
        # error path.
        status_code = 0
    body = body.strip()
    if not body:
        return status_code, None
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return status_code, None
    # json.loads() may return a list or a scalar. SubResponse.body is typed
    # ``dict | None``; a non-dict shape must degrade to None rather than being
    # carried through into a strict pydantic model it was never declared for.
    return status_code, parsed if isinstance(parsed, dict) else None


def decode_multipart(content: bytes, content_type: str) -> list[SubResponse]:
    """Decode a ``multipart/mixed`` body into its sub-responses.

    Order is preserved, but callers should correlate via ``content_id`` rather
    than position — the specification does not promise the server answers in the
    order it was asked.

    :param content:      The raw response body.
    :param content_type: The response Content-Type header, carrying the boundary.
    :return:             One entry per part, in the order they appear.
    """
    message = BytesParser(policy=HTTP).parsebytes(
        b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n" + content
    )

    sub_responses: list[SubResponse] = []
    for part in message.iter_parts():
        raw_content_id = part.get("Content-ID")
        content_id = None
        if raw_content_id:
            # Google echoes "<response-item-0>" for our "<item-0>".
            content_id = raw_content_id.strip("<>").removeprefix("response-")
        status_code, body = _parse_http_payload(part.get_payload())
        sub_responses.append(
            SubResponse(
                content_id=content_id,
                status_code=status_code,
                body=body,
            )
        )
    return sub_responses
