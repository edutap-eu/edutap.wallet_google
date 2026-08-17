# Batch Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `batch_update(name, data)` and `abatch_update(name, data)` — one
`multipart/mixed` request that PATCHes many wallet objects of any pass type in a single
API call.

**Architecture:** Three pieces, no more. A pure encoder/decoder for `multipart/mixed`
that knows nothing about wallet models; two API functions that turn a list of plain dicts
into sub-requests and return one result per input item in input order; and a new settings
entry for the batch endpoint. No chunking, no throttling, no retry, no resume — those are
a later stage and deliberately out of scope.

**Tech Stack:** Python 3.12+, Pydantic v2, httpx, authlib, pytest, respx, the `email`
module from the standard library for multipart parsing.

**Spec:** None as a separate file. The design rationale lives in the *Design decisions*
section below; it was settled in conversation on 2026-08-17 and the reasoning is short
enough to travel with the plan.

## Global Constraints

- Branch: `feature/batch-update`, already created from `main`. Never commit to `main`.
  Never `git push` — the user pushes.
- Conventional Commits. Commit messages, comments, identifiers and docstrings in English.
- No new runtime dependencies. `email` and `uuid` are standard library; everything else is
  already required.
- Public functions carry full type hints. The package ships `py.typed`.
- Sync and async are both public and behave identically; async functions carry the `a`
  prefix, matching every other function in `api.py`.
- Rate limit for context: the Google Wallet API allows **20 calls per second**
  ([FAQ](https://developers.google.com/wallet/generic/resources/faq)). Nothing in this
  plan enforces it — the caller does.
- Every task ends green on `uvx tox -e py313` and `uvx tox -e lint`.

## What is known, and how well

This matters because two of the numbers driving this design are not in Google's
documentation, and the code should not pretend otherwise.

- **Documented:** the batch endpoint is `POST https://walletobjects.googleapis.com/batch`
  with a `multipart/mixed` body; the resource path inside each part is
  `/walletobjects/v1/<url_part>`; the mechanism is identical across generic passes,
  loyalty cards and event tickets (checked on all three pages). Rate limit 20 calls/s.
- **Not documented anywhere:** the maximum number of sub-requests per batch, and whether
  a batch counts as one call or as N against the rate limit. Searched for both; the
  Wallet pages and the FAQ are silent.
- **Supplied by the maintainer, 2026-08-17:** a batch counts as **one** request regardless
  of how many sub-requests it carries. This is why batching is worth building at all — it
  turns 70,000 daily updates from roughly an hour of wall-clock into minutes. Record it in
  code comments as what it is: an operational finding, not a documented guarantee. Do not
  cite a Google URL for it, because there isn't one.

Consequence for the code: **no sub-request count is hard-coded anywhere.** The functions
take whatever list they are given. If a ceiling exists, it will surface as an HTTP error
from Google, and the caller decides what to do about it.

## Design decisions

**`batch_update` takes a `name` plus plain dicts, not model instances.** `update()` today
derives the type from the instance via `lookup_metadata_by_model_instance()`, which is why
it needs a real model. `read()` and `listing()` take `name` explicitly instead. Batch
follows `read()`: the caller passes `"LoyaltyObject"` and a list of dicts. This removes
the required-field problem entirely — a PATCH carrying two changed attributes does not
need a `classId` just to satisfy the constructor.

**Payloads are validated against a partial model.** `make_partial_model()` already exists
(built for partial responses) and turns required fields optional while staying a subclass.
Validating each dict through it catches typos and type errors *before* the network call,
without demanding fields the caller has no reason to send. Serialisation then reuses the
existing path, which already sets `exclude_unset=True` — so only the attributes the caller
actually set go on the wire.

**All pass types come for free.** Every registered model already carries a `url_part`
(`genericObject`, `loyaltyObject`, `eventTicketObject`, …). The sub-request path is a
registry lookup, so nothing is generic-pass-specific.

**Results never raise on partial failure.** A batch is not atomic. `batch_update` returns
one `BatchResult` per input item, in input order. Exceptions are reserved for the batch
request itself failing.

**Results carry raw dicts, not parsed models.** Parsing 1000 responses into full models
costs time for information the caller of a bulk update rarely wants. `BatchResult.body`
is the decoded JSON. Parsing can be added later without breaking the signature.

## File Structure

| File | Responsibility | Task |
| --- | --- | --- |
| `src/edutap/wallet_google/batch.py` | encode/decode `multipart/mixed`; knows nothing about wallet models (create) | 1 |
| `tests/test_batch_multipart.py` | encoder/decoder tests, no network (create) | 1 |
| `src/edutap/wallet_google/models/misc.py` | `BatchResult`, `BatchError` (modify) | 2 |
| `src/edutap/wallet_google/settings.py` | `batch_url` setting (modify) | 2 |
| `src/edutap/wallet_google/api.py` | `batch_update`, `abatch_update` (modify) | 2, 3 |
| `tests/test_api_batch.py` | `batch_update` against respx (create) | 2 |
| `tests/test_api_batch_async.py` | `abatch_update` against respx (create) | 3 |
| `docs/tutorials.md`, `docs/reference.md` | document the new functions (modify) | 4 |

---

### Task 1: The multipart encoder and decoder

Pure functions over bytes. No httpx, no models, no settings. This is the only part of the
feature with fiddly format details, and it is fully testable without a network.

**Files:**
- Create: `src/edutap/wallet_google/batch.py`
- Create: `tests/test_batch_multipart.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `BatchSubRequest` — dataclass with `method: str`, `path: str`, `body: str | None`,
    `content_id: str`.
  - `BatchSubResponse` — dataclass with `content_id: str | None`, `status_code: int`,
    `body: dict | None`.
  - `encode_batch_request(sub_requests: list[BatchSubRequest], boundary: str) -> bytes`
  - `decode_batch_response(content: bytes, content_type: str) -> list[BatchSubResponse]`
  - `make_boundary() -> str`

**Format note, read before implementing.** Google's Wallet examples show each part with
`Content-Type: application/json` followed by the request line. Google's general batch
protocol uses `Content-Type: application/http` for the parts. The Wallet pages are what we
have, so encode as they show, and keep the part content type in the module-level constant
`_PART_CONTENT_TYPE` so switching it is a one-line change. Task 5's integration test is
what settles which one the server actually accepts.

- [ ] **Step 1: Write the failing encoder test**

```python
"""Tests for multipart/mixed encoding and decoding of batch requests."""

from edutap.wallet_google.batch import BatchSubRequest
from edutap.wallet_google.batch import encode_batch_request


def test_encode_produces_one_part_per_sub_request():
    """Each sub-request becomes a delimited part carrying method, path and body."""
    sub_requests = [
        BatchSubRequest(
            method="PATCH",
            path="/walletobjects/v1/genericObject/issuer.one",
            body='{"state":"EXPIRED"}',
            content_id="item-0",
        ),
        BatchSubRequest(
            method="PATCH",
            path="/walletobjects/v1/genericObject/issuer.two",
            body='{"state":"ACTIVE"}',
            content_id="item-1",
        ),
    ]

    encoded = encode_batch_request(sub_requests, boundary="testboundary").decode("utf-8")

    assert encoded.count("--testboundary\r\n") == 2
    assert encoded.endswith("--testboundary--\r\n")
    assert "Content-ID: <item-0>" in encoded
    assert "Content-ID: <item-1>" in encoded
    assert "PATCH /walletobjects/v1/genericObject/issuer.one" in encoded
    assert '{"state":"EXPIRED"}' in encoded
```

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_batch_multipart.py::test_encode_produces_one_part_per_sub_request -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'edutap.wallet_google.batch'`

- [ ] **Step 3: Write the encoder**

Create `src/edutap/wallet_google/batch.py`:

```python
"""Encoding and decoding of ``multipart/mixed`` batch requests.

This module deliberately knows nothing about wallet models, settings or HTTP
clients. It turns sub-requests into bytes and bytes back into sub-responses,
which makes the fiddly format details testable without a network.

See https://developers.google.com/wallet/generic/resources/performance-tips
"""

from dataclasses import dataclass

import json
import uuid


# Google's Wallet examples show the parts as application/json. Google's general
# batch protocol uses application/http. The Wallet documentation is what we have,
# so follow it — and keep it in one place so it is a one-line change if the
# server turns out to want the other one.
_PART_CONTENT_TYPE = "application/json"

# multipart requires CRLF line endings (RFC 2046).
_CRLF = "\r\n"


@dataclass
class BatchSubRequest:
    """A single HTTP request to be carried inside a batch."""

    method: str
    path: str
    body: str | None
    content_id: str


@dataclass
class BatchSubResponse:
    """A single HTTP response extracted from a batch response."""

    content_id: str | None
    status_code: int
    body: dict | None


def make_boundary() -> str:
    """Return a boundary that cannot collide with the payload."""
    return f"batch_{uuid.uuid4().hex}"


def encode_batch_request(
    sub_requests: list[BatchSubRequest],
    boundary: str,
) -> bytes:
    """Encode sub-requests as a ``multipart/mixed`` body.

    :param sub_requests: The requests to carry, in order.
    :param boundary:     Delimiter between the parts, without leading dashes.
    :return:             The encoded body, ready to be sent as the request content.
    """
    lines: list[str] = []
    for sub_request in sub_requests:
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
```

- [ ] **Step 4: Run it and watch it pass**

Run: `uv run pytest tests/test_batch_multipart.py -v`
Expected: PASS

- [ ] **Step 5: Write the failing decoder test**

Append to `tests/test_batch_multipart.py`:

```python
from edutap.wallet_google.batch import decode_batch_response


BATCH_RESPONSE = (
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
    responses = decode_batch_response(
        BATCH_RESPONSE.encode("utf-8"),
        "multipart/mixed; boundary=rspboundary",
    )

    assert len(responses) == 2
    assert responses[0].status_code == 200
    assert responses[0].content_id == "item-0"
    assert responses[0].body == {"id": "issuer.one", "state": "EXPIRED"}
    assert responses[1].status_code == 404
    assert responses[1].content_id == "item-1"
    assert responses[1].body["error"]["code"] == 404


def test_decode_strips_the_response_prefix_from_content_id():
    """Google echoes Content-ID with a 'response-' prefix; we map back to ours."""
    responses = decode_batch_response(
        BATCH_RESPONSE.encode("utf-8"),
        "multipart/mixed; boundary=rspboundary",
    )

    assert [r.content_id for r in responses] == ["item-0", "item-1"]
```

- [ ] **Step 6: Run them and watch them fail**

Run: `uv run pytest tests/test_batch_multipart.py -v`
Expected: FAIL — `ImportError: cannot import name 'decode_batch_response'`

- [ ] **Step 7: Write the decoder**

Append to `src/edutap/wallet_google/batch.py`:

```python
def _parse_http_payload(payload: str) -> tuple[int, dict | None]:
    """Parse an embedded HTTP response into status code and JSON body.

    :param payload: A raw HTTP response: status line, headers, blank line, body.
    :return:        Tuple of status code and decoded body (None when not JSON).
    """
    head, _, body = payload.partition(f"{_CRLF}{_CRLF}")
    status_line = head.split(_CRLF, 1)[0]
    # "HTTP/1.1 404 Not Found" -> 404
    status_code = int(status_line.split(" ")[1])
    body = body.strip()
    if not body:
        return status_code, None
    try:
        return status_code, json.loads(body)
    except json.JSONDecodeError:
        return status_code, None


def decode_batch_response(content: bytes, content_type: str) -> list[BatchSubResponse]:
    """Decode a ``multipart/mixed`` batch response into its sub-responses.

    Order is preserved, but callers should correlate via ``content_id`` rather
    than position — the specification does not promise the server answers in the
    order it was asked.

    :param content:      The raw response body.
    :param content_type: The response Content-Type header, carrying the boundary.
    :return:             One entry per part, in the order they appear.
    """
    from email.parser import BytesParser
    from email.policy import HTTP

    message = BytesParser(policy=HTTP).parsebytes(
        b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n" + content
    )

    sub_responses: list[BatchSubResponse] = []
    for part in message.iter_parts():
        raw_content_id = part.get("Content-ID")
        content_id = None
        if raw_content_id:
            # Google echoes "<response-item-0>" for our "<item-0>".
            content_id = raw_content_id.strip("<>").removeprefix("response-")
        status_code, body = _parse_http_payload(part.get_payload())
        sub_responses.append(
            BatchSubResponse(
                content_id=content_id,
                status_code=status_code,
                body=body,
            )
        )
    return sub_responses
```

Move the two `email` imports to the top of the module with the other imports before
committing — they are inline here only to keep the diff readable.

- [ ] **Step 8: Run the whole file**

Run: `uv run pytest tests/test_batch_multipart.py -v`
Expected: PASS, 3 tests

- [ ] **Step 9: Lint and commit**

```bash
uvx ruff format src/edutap/wallet_google/batch.py tests/test_batch_multipart.py
uvx ruff check src/edutap/wallet_google/batch.py tests/test_batch_multipart.py
git add src/edutap/wallet_google/batch.py tests/test_batch_multipart.py
git commit -m "feat(batch): add multipart/mixed encoder and decoder"
```

---

### Task 2: `batch_update()` — the synchronous API function

**Files:**
- Modify: `src/edutap/wallet_google/settings.py`
- Modify: `src/edutap/wallet_google/models/misc.py`
- Modify: `src/edutap/wallet_google/api.py`
- Create: `tests/test_api_batch.py`

**Interfaces:**
- Consumes: `BatchSubRequest`, `BatchSubResponse`, `encode_batch_request`,
  `decode_batch_response`, `make_boundary` from Task 1.
- Produces:
  - `BatchError` — Pydantic model with `code: int`, `message: str`, `status: str | None`.
  - `BatchResult` — Pydantic model with `index: int`, `resource_id: str`,
    `status_code: int`, `body: dict | None`, `error: BatchError | None`, and a
    property `ok: bool`.
  - `batch_update(name: str, data: list[dict], *, credentials: dict | None = None) -> list[BatchResult]`
  - `settings.batch_url`

- [ ] **Step 1: Write the failing test**

Create `tests/test_api_batch.py`:

```python
"""Tests for batch_update()."""

from edutap.wallet_google.api import batch_update
from edutap.wallet_google.settings import Settings

import httpx
import pytest
import respx


BATCH_RESPONSE = (
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


@respx.mock
def test_batch_update_sends_one_request_and_returns_one_result_per_item(mock_session):
    """Two updates go out as a single POST and come back as two results."""
    route = respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=BATCH_RESPONSE.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )

    results = batch_update(
        "GenericObject",
        [
            {"id": "issuer.one", "state": "EXPIRED"},
            {"id": "issuer.two", "state": "ACTIVE"},
        ],
    )

    assert route.call_count == 1
    assert len(results) == 2
    assert results[0].ok is True
    assert results[0].resource_id == "issuer.one"
    assert results[0].body["state"] == "EXPIRED"
    assert results[1].ok is False
    assert results[1].error.code == 404
    assert results[1].error.message == "not found"


@respx.mock
def test_batch_update_sends_only_the_attributes_that_were_set(mock_session):
    """A two-attribute PATCH must not carry the rest of the model."""
    route = respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=BATCH_RESPONSE.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )

    batch_update("GenericObject", [{"id": "issuer.one", "state": "EXPIRED"}])

    body = route.calls.last.request.content.decode("utf-8")
    assert '"state"' in body
    assert '"classId"' not in body
    assert "PATCH /walletobjects/v1/genericObject/issuer.one" in body


def test_batch_update_rejects_an_unknown_attribute(mock_session):
    """Typos are caught before the network call, not by Google."""
    with pytest.raises(ValueError) as exc_info:
        batch_update("GenericObject", [{"id": "issuer.one", "notAField": 1}])

    assert "notAField" in str(exc_info.value)


def test_batch_update_requires_the_resource_id(mock_session):
    """Without an id there is nothing to PATCH."""
    with pytest.raises(ValueError) as exc_info:
        batch_update("GenericObject", [{"state": "EXPIRED"}])

    assert "id" in str(exc_info.value)
```

- [ ] **Step 2: Run and watch it fail**

Run: `uv run pytest tests/test_api_batch.py -v`
Expected: FAIL — `ImportError: cannot import name 'batch_update'`

- [ ] **Step 3: Add the settings entry**

In `src/edutap/wallet_google/settings.py`, beside `API_URL`:

```python
BATCH_URL = "https://walletobjects.googleapis.com/batch"
```

and in the `Settings` class, beside `api_url`:

```python
    batch_url: AnyHttpUrl = AnyHttpUrl(BATCH_URL)
```

Note it is *not* derived from `api_url`: the batch endpoint sits one level above
`/walletobjects/v1`, so appending would produce the wrong URL.

- [ ] **Step 4: Add the result models**

Append to `src/edutap/wallet_google/models/misc.py`:

```python
class BatchError(Model):
    """The error Google reports for a single failed sub-request."""

    code: int
    message: str
    status: str | None = None


class BatchResult(Model):
    """The outcome of one sub-request, correlated back to its input item."""

    index: int
    resource_id: str
    status_code: int
    body: dict | None = None
    error: BatchError | None = None

    @property
    def ok(self) -> bool:
        """True when Google accepted this sub-request."""
        return self.error is None and 200 <= self.status_code < 300
```

- [ ] **Step 5: Implement `batch_update`**

Add to `src/edutap/wallet_google/api.py`, and add `"batch_update"` and `"abatch_update"`
to `__all__`:

```python
def _prepare_batch_update(
    name: str,
    data: list[dict[str, typing.Any]],
) -> tuple[list[BatchSubRequest], list[str]]:
    """Turn dicts into batch sub-requests.

    Payloads are validated against a partial model: field names and types are
    checked, but required fields are not demanded — a PATCH carrying two changed
    attributes has no reason to supply a classId.

    :param name: Registered model name, e.g. "GenericObject" or "LoyaltyObject".
    :param data: One dict per object, each carrying at least the resource id.
    :return:     Tuple of sub-requests and their resource ids, in input order.
    :raises ValueError: When a payload is invalid or carries no resource id.
    """
    metadata = lookup_metadata_by_name(name)
    raise_when_operation_not_allowed(name, "update")
    partial_model = make_partial_model(metadata["model"])
    resource_id_key = metadata["resource_id"]
    api_path = urllib.parse.urlparse(str(client_pool.settings.api_url)).path

    sub_requests: list[BatchSubRequest] = []
    resource_ids: list[str] = []
    for index, item in enumerate(data):
        resource_id = item.get(resource_id_key)
        if not resource_id:
            raise ValueError(
                f"Item {index} has no '{resource_id_key}'; there is nothing to update."
            )
        try:
            verified = partial_model.model_validate(item)
        except PydanticValidationError as exc:
            raise ValueError(f"Item {index} is not valid for '{name}': {exc}") from exc
        body = verified.model_dump_json(exclude_unset=True, by_alias=True)
        sub_requests.append(
            BatchSubRequest(
                method="PATCH",
                path=f"{api_path}/{metadata['url_part']}/{resource_id}",
                body=body,
                content_id=f"item-{index}",
            )
        )
        resource_ids.append(resource_id)
    return sub_requests, resource_ids


def _build_batch_results(
    sub_responses: list[BatchSubResponse],
    resource_ids: list[str],
) -> list[BatchResult]:
    """Correlate sub-responses back to their input items.

    Correlation is by Content-ID, not by position: the batch specification does
    not promise the server answers in the order it was asked.
    """
    by_content_id = {r.content_id: r for r in sub_responses if r.content_id}
    results: list[BatchResult] = []
    for index, resource_id in enumerate(resource_ids):
        sub_response = by_content_id.get(f"item-{index}")
        if sub_response is None:
            # No part came back for this item at all.
            results.append(
                BatchResult(
                    index=index,
                    resource_id=resource_id,
                    status_code=0,
                    error=BatchError(
                        code=0, message="No response part for this sub-request."
                    ),
                )
            )
            continue
        body = sub_response.body
        error = None
        if body is not None and "error" in body:
            error = BatchError.model_validate(body["error"])
            body = None
        results.append(
            BatchResult(
                index=index,
                resource_id=resource_id,
                status_code=sub_response.status_code,
                body=body,
                error=error,
            )
        )
    return results


def batch_update(
    name: str,
    data: list[dict[str, typing.Any]],
    *,
    credentials: dict | None = None,
) -> list[BatchResult]:
    """Update many wallet objects of one type in a single API call.

    Sends one ``multipart/mixed`` request carrying a PATCH per item. Works for
    every registered pass type — the path comes from the registry, so
    "GenericObject", "LoyaltyObject", "EventTicketObject" and the rest behave
    identically.

    Only the attributes present in each dict are sent, so a batch of small
    changes stays small on the wire.

    This function does not chunk, throttle or retry. The Google Wallet API is
    rate limited to 20 calls per second; staying within it is the caller's
    business.

    :param name:        Registered model name, e.g. "LoyaltyObject".
    :param data:        One dict per object, each carrying at least the resource id.
    :param credentials: Optional session credentials as dict.
    :raises ValueError: When a payload is invalid or carries no resource id.
    :raises WalletException: When the batch request itself fails. Individual
                        sub-request failures do **not** raise — they come back
                        as results with an ``error``.
    :return:            One result per input item, in input order.
    """
    if not data:
        return []
    sub_requests, resource_ids = _prepare_batch_update(name, data)
    boundary = make_boundary()

    client = client_pool.client(credentials=credentials)
    response = client.post(
        url=str(client_pool.settings.batch_url),
        content=encode_batch_request(sub_requests, boundary),
        headers={"Content-Type": f"multipart/mixed; boundary={boundary}"},
    )
    handle_response_errors(response, "batch_update", name, f"{len(data)} items")

    sub_responses = decode_batch_response(
        response.content, response.headers.get("Content-Type", "")
    )
    return _build_batch_results(sub_responses, resource_ids)
```

Add these imports at the top of `api.py`:

```python
from .batch import BatchSubRequest
from .batch import BatchSubResponse
from .batch import decode_batch_response
from .batch import encode_batch_request
from .batch import make_boundary
from .models.misc import BatchError
from .models.misc import BatchResult
from pydantic import ValidationError as PydanticValidationError

import urllib.parse
```

- [ ] **Step 6: Run and watch it pass**

Run: `uv run pytest tests/test_api_batch.py -v`
Expected: PASS, 4 tests

- [ ] **Step 7: Run the whole suite for regressions**

Run: `uvx tox -e py313`
Expected: PASS — `api.py` and `misc.py` both changed, so everything gets a look.

- [ ] **Step 8: Lint and commit**

```bash
uvx ruff format src tests
uvx ruff check src tests
git add src/edutap/wallet_google/api.py src/edutap/wallet_google/models/misc.py src/edutap/wallet_google/settings.py tests/test_api_batch.py
git commit -m "feat(batch): add batch_update() for all pass types"
```

---

### Task 3: `abatch_update()` — the asynchronous twin

**Files:**
- Modify: `src/edutap/wallet_google/api.py`
- Create: `tests/test_api_batch_async.py`

**Interfaces:**
- Consumes: `_prepare_batch_update`, `_build_batch_results`, `BatchResult` from Task 2.
- Produces: `abatch_update(name: str, data: list[dict], *, credentials: dict | None = None) -> list[BatchResult]`

- [ ] **Step 1: Write the failing test**

Create `tests/test_api_batch_async.py` with the same `BATCH_RESPONSE` constant as
`tests/test_api_batch.py` (repeat it — the two files are read independently), then:

```python
"""Tests for abatch_update()."""

from edutap.wallet_google.api import abatch_update
from edutap.wallet_google.settings import Settings

import httpx
import pytest
import respx


@pytest.mark.asyncio
@respx.mock
async def test_abatch_update_matches_the_sync_behaviour(mock_async_session):
    """One POST, one result per item, failures reported not raised."""
    route = respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=BATCH_RESPONSE.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )

    results = await abatch_update(
        "LoyaltyObject",
        [
            {"id": "issuer.one", "state": "EXPIRED"},
            {"id": "issuer.two", "state": "ACTIVE"},
        ],
    )

    assert route.call_count == 1
    assert len(results) == 2
    assert results[0].ok is True
    assert results[1].ok is False
    assert results[1].error.code == 404
```

The marker is `@pytest.mark.asyncio`, matching every async test in
`tests/test_api_async.py`. The repository uses `pytest-asyncio`, not `anyio` — do not
introduce a second convention here.

- [ ] **Step 2: Run and watch it fail**

Run: `uv run pytest tests/test_api_batch_async.py -v`
Expected: FAIL — `ImportError: cannot import name 'abatch_update'`

- [ ] **Step 3: Implement it**

Add to `api.py`, in the asynchronous section beside the other `a`-prefixed functions:

```python
async def abatch_update(
    name: str,
    data: list[dict[str, typing.Any]],
    *,
    credentials: dict | None = None,
) -> list[BatchResult]:
    """Asynchronously update many wallet objects of one type in a single API call.

    See :func:`batch_update` for the full description; behaviour is identical.

    :param name:        Registered model name, e.g. "LoyaltyObject".
    :param data:        One dict per object, each carrying at least the resource id.
    :param credentials: Optional session credentials as dict.
    :raises ValueError: When a payload is invalid or carries no resource id.
    :raises WalletException: When the batch request itself fails.
    :return:            One result per input item, in input order.
    """
    if not data:
        return []
    sub_requests, resource_ids = _prepare_batch_update(name, data)
    boundary = make_boundary()

    client = client_pool.async_client(credentials=credentials)
    response = await client.post(
        url=str(client_pool.settings.batch_url),
        content=encode_batch_request(sub_requests, boundary),
        headers={"Content-Type": f"multipart/mixed; boundary={boundary}"},
    )
    handle_response_errors(response, "batch_update", name, f"{len(data)} items")

    sub_responses = decode_batch_response(
        response.content, response.headers.get("Content-Type", "")
    )
    return _build_batch_results(sub_responses, resource_ids)
```

- [ ] **Step 4: Run and watch it pass**

Run: `uv run pytest tests/test_api_batch_async.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
uvx ruff format src tests
uvx ruff check src tests
git add src/edutap/wallet_google/api.py tests/test_api_batch_async.py
git commit -m "feat(batch): add abatch_update()"
```

---

### Task 4: Prove it across every pass type, and document it

The claim "works for all pass types" is currently an argument about the registry. This
task turns it into a test, and writes the docs.

**Files:**
- Modify: `tests/test_api_batch.py`
- Modify: `docs/tutorials.md`
- Modify: `docs/reference.md`

**Interfaces:**
- Consumes: `batch_update` from Task 2.
- Produces: no new code interfaces.

- [ ] **Step 1: Write the parametrised failing test**

Append to `tests/test_api_batch.py`:

```python
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
def test_batch_update_builds_the_right_path_for_every_pass_type(
    mock_session, name, url_part
):
    """The sub-request path comes from the registry, so every type works."""
    route = respx.post(str(Settings().batch_url)).mock(
        return_value=httpx.Response(
            200,
            content=BATCH_RESPONSE.encode("utf-8"),
            headers={"Content-Type": "multipart/mixed; boundary=rspboundary"},
        )
    )

    batch_update(name, [{"id": "issuer.one", "state": "EXPIRED"}])

    body = route.calls.last.request.content.decode("utf-8")
    assert f"PATCH /walletobjects/v1/{url_part}/issuer.one" in body
```

- [ ] **Step 2: Run it**

Run: `uv run pytest tests/test_api_batch.py -k every_pass_type -v`
Expected: PASS for all seven. If a type fails because `state` is not one of its fields,
replace the payload for that type with an attribute it does have — do not weaken the
assertion on the path.

- [ ] **Step 3: Document it in the tutorial**

Add a section to `docs/tutorials.md`, after the update section:

````markdown
## Updating many passes at once

`batch_update()` sends one request carrying a PATCH per object. It works for every pass
type, and only the attributes you set are sent:

```python
from edutap.wallet_google import api

results = api.batch_update(
    "LoyaltyObject",
    [
        {"id": "issuer.member-1", "state": "EXPIRED"},
        {"id": "issuer.member-2", "state": "EXPIRED"},
    ],
)

for result in results:
    if not result.ok:
        print(f"{result.resource_id} failed: {result.error.message}")
```

A batch is **not** atomic: individual items can fail while the rest succeed, which is why
failures come back as results rather than exceptions. There is one result per input item,
in input order.

`batch_update()` does not split, throttle or retry. The Google Wallet API is rate limited
to 20 calls per second; deciding how many objects go into one batch, and how fast batches
follow each other, is yours.

The asynchronous twin is `await api.abatch_update(...)` and behaves identically.
````

- [ ] **Step 4: Add the functions to the reference**

Add `batch_update` and `abatch_update` to `docs/reference.md`, following whatever
structure the surrounding entries use.

- [ ] **Step 5: Check the Markdown renders**

There is **no** documentation build in this repository — `docs/` holds plain Markdown and
is built centrally for docs.edutap.eu. So there is no `tox -e docs` to run. Instead, read
the two files back and check the fenced code blocks are balanced and the headings sit at
the same level as their neighbours.

- [ ] **Step 6: Commit**

```bash
git add tests/test_api_batch.py docs/tutorials.md docs/reference.md
git commit -m "docs(batch): document batch_update and cover all pass types"
```

---

### Task 5: The integration test that settles the open format question

Task 1 encodes the parts as `Content-Type: application/json` because that is what Google's
Wallet examples show, while Google's general batch protocol uses `application/http`. Only
the real endpoint can say which it accepts. This task is also the first measurement of how
many sub-requests actually fit.

**Files:**
- Create: `tests/integration/test_batch.py`

**Interfaces:**
- Consumes: `batch_update` from Task 2.
- Produces: no new code interfaces.

- [ ] **Step 1: Read how the existing integration tests are set up**

Read `tests/integration/test_CRULM.py`. Follow its credential handling, its
`@pytest.mark.integration` marking and its issuer-id fixture exactly.

- [ ] **Step 2: Write the round-trip test**

Create `tests/integration/test_batch.py`. It must create two objects, batch-update one
attribute on both, assert both results are `ok`, then read them back and assert the
attribute actually changed. Reading back matters: a 200 in a batch part is not by itself
proof the write landed.

- [ ] **Step 3: Run it against the real API**

Run: `uvx tox -e py313 -- tests/integration/test_batch.py -v --run-integration`

If it fails with a 400 on the format, switch `_PART_CONTENT_TYPE` in `batch.py` to
`"application/http"` and — because that content type means each part carries a full HTTP
message — the request line then needs an HTTP version suffix (`PATCH <path> HTTP/1.1`) and
its own `Content-Type: application/json` header before the body. Adjust the Task 1 tests
to match, then re-run.

- [ ] **Step 4: Measure the ceiling**

Still in the integration environment, not as a committed test: run `batch_update` with
growing item counts (50, 200, 500, 1000) and record where it starts failing, and with what
error.

- [ ] **Step 5: Write the measurement down**

Add a short section to this plan file recording the numbers, dated, and labelled
**measured** — what the endpoint did on the day we looked, not what Google guarantees.
Anyone sizing a batch later needs to know which of those it is.

- [ ] **Step 6: Commit**

```bash
git add tests/integration/test_batch.py superpowers/plans/2026-08-17-batch-update.md
git commit -m "test(batch): add integration round-trip and record measured limits"
```

---

## Verification

- [ ] `uvx tox -e py313` green.
- [ ] `uvx tox -e lint` green.
- [ ] Integration test green against the real API.
- [ ] The measured sub-request ceiling is recorded in this file, labelled as measured.

## Deliberately out of scope

Each of these is a plausible next stage, and none belongs in this one:

- **The driver** — chunking, throttling to 20 calls/s, retry, resume, progress reporting.
  This is where a daily 70,000-object reconciliation actually gets decided, and it wants
  its own design once the measured batch ceiling is known.
- **`batch_create` and mixed-operation batches.** `BatchSubRequest` already carries the
  method, so create is a small addition later; nothing here blocks it.
- **Parsing results into models.** `BatchResult.body` stays a dict; adding a parsed model
  later does not break the signature.
- **Delta detection.** Writing only genuinely changed objects would cut the daily volume
  far more than batching does, but it belongs in the calling system, not in this library.
