# Batch Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `Batch` object that collects sub-requests and sends them as one
`multipart/mixed` request, PATCHing many wallet objects — of any pass type, mixed freely —
in a single API call.

**Architecture:** Two modules and one class. `multipart.py` encodes and decodes
`multipart/mixed` and knows nothing about wallet models. `batch.py` holds the public
`Batch` class: you fill it with `add_update()` calls and then `execute()` it. One `Batch`
is one HTTP request. No chunking, no throttling, no retry, no resume — those come later
as keyword arguments to `execute()`.

**Tech Stack:** Python 3.12+, Pydantic v2, httpx, authlib, pytest, respx, the `email`
module from the standard library for multipart parsing.

**Spec:** None as a separate file. The design rationale lives in the *Design decisions*
section below; it was settled in conversation on 2026-08-17 and is short enough to travel
with the plan.

## Global Constraints

- Branch: `feature/batch-update`, already created from `main`. Never commit to `main`.
  Never `git push` — the user pushes.
- Conventional Commits. Commit messages, comments, identifiers and docstrings in English.
- No new runtime dependencies. `email` and `uuid` are standard library; everything else is
  already required.
- Public functions and methods carry full type hints. The package ships `py.typed`.
- Sync and async are both public and behave identically; async carries the `a` prefix,
  matching every other function in `api.py`.
- Every parameter of `execute()` and `aexecute()` is **keyword-only**, so the later driver
  stage can add `chunk_size` and friends without breaking existing calls.
- Rate limit for context: the Google Wallet API allows **20 calls per second**
  ([FAQ](https://developers.google.com/wallet/generic/resources/faq)). Nothing in this
  plan enforces it — the caller does.
- Every task ends green on `uvx tox -e py313` and `uvx tox -e lint`.

## What is known, and how well

Two of the numbers driving this design are not in Google's documentation, and the code
should not pretend otherwise.

- **Documented:** the batch endpoint is `POST https://walletobjects.googleapis.com/batch`
  with a `multipart/mixed` body; the resource path inside each part is
  `/walletobjects/v1/<url_part>`; the mechanism is identical across generic passes,
  loyalty cards and event tickets (checked on all three pages). Rate limit 20 calls/s.
- **Not documented anywhere:** the maximum number of sub-requests per batch, and whether
  a batch counts as one call or as N against the rate limit. Searched for both; the
  Wallet pages and the FAQ are silent.
- **Operational finding, not a documented guarantee** (maintainer, 2026-08-17): a batch
  counts as **one** request regardless of how many sub-requests it carries. This is why
  batching is worth building — it turns 70,000 daily updates from roughly an hour of
  wall-clock into minutes. Task 5 verifies it against the Cloud Console. Do not cite a
  Google URL for it; there isn't one.

Consequence for the code: **no sub-request count is hard-coded anywhere.** A `Batch` takes
whatever it is given. If a ceiling exists, it surfaces as an HTTP error from Google, and
the caller decides what to do about it.

## Design decisions

**A `Batch` is an object you fill and then execute.** This mirrors the endpoint: every
part of the multipart body carries its own method and path, so there is no technical
reason for the parts to share a pass type. It also makes the boundary visible — filling a
`Batch` and calling `execute()` makes it obvious that one HTTP request is being built,
where a function taking a 70,000-item list would hide that it produces a single request
running straight into a ceiling nobody has measured.

**Sub-requests carry a `name` plus a plain dict, not a model instance.** `update()` today
derives the type from the instance via `lookup_metadata_by_model_instance()`, which is why
it needs a real model. `read()` and `listing()` take `name` explicitly instead. `Batch`
follows `read()`, which removes the required-field problem: a PATCH carrying two changed
attributes does not need a `classId` just to satisfy the constructor.

**Validation happens in `add_update()`, not in `execute()`.** A typo then fails on the
line that caused it, with the item's own name attached, rather than surfacing at the end
of a 1000-item loop. Validation runs against `make_partial_model()`, which already exists
(built for partial responses) and turns required fields optional while staying a subclass.
Serialisation reuses the existing path, which already sets `exclude_unset=True` — so only
the attributes the caller actually set go on the wire.

**All pass types come for free, and may be mixed.** Every registered model carries a
`url_part` (`genericObject`, `loyaltyObject`, `eventTicketObject`, …), so the sub-request
path is a registry lookup.

**Results never raise on partial failure.** A batch is not atomic. `execute()` returns one
`BatchResult` per added sub-request, in the order they were added. Exceptions are reserved
for the batch request itself failing.

**Add order is the result order; wire order is an implementation detail.** `Batch` is free
to group and sort its sub-requests internally before encoding — currently a stable group
by pass type — and that freedom costs nothing, because results are correlated back by
`Content-ID` rather than by position. The same correlation already had to exist for a
different reason: the specification does not promise the server answers in the order it
was asked. One mechanism, two problems solved.

State the invariant plainly, because it is the thing that must not break as the internal
ordering changes: **whatever `Batch` does to the order on the wire, `execute()` returns
results in the order items were added.** Task 2 has a test that holds this down against a
server answering in a deliberately shuffled order.

Whether grouping actually makes Google faster is unmeasured and, honestly, unlikely to be
dramatic — the reason to build it in now is that retrofitting reordering onto a design
that had promised wire order would be a breaking change, while allowing it from the start
costs three lines.

**Results carry raw dicts, not parsed models.** Parsing 1000 responses into full models
costs time for information a bulk update rarely wants. `BatchResult.body` is the decoded
JSON. Parsing can be added later without breaking the signature.

**`execute()` is a method, and every parameter is keyword-only.** The later driver stage
adds `chunk_size`, rate limiting and retry as keyword arguments. `chunk_size=None` means
one request, today and after that change — so the semantics stay stable as the feature
grows.

## File Structure

| File | Responsibility | Task |
| --- | --- | --- |
| `src/edutap/wallet_google/multipart.py` | encode/decode `multipart/mixed`; knows nothing about wallet models (create) | 1 |
| `tests/test_multipart.py` | encoder/decoder tests, no network (create) | 1 |
| `src/edutap/wallet_google/batch.py` | the public `Batch` class plus `BatchResult` and `BatchError` (create) | 2, 3 |
| `src/edutap/wallet_google/settings.py` | `batch_url` setting (modify) | 2 |
| `src/edutap/wallet_google/api.py` | re-export `Batch` so `api.Batch()` works (modify) | 2 |
| `tests/test_batch.py` | building and executing a batch, against respx (create) | 2, 4 |
| `tests/test_batch_async.py` | `aexecute()` against respx (create) | 3 |
| `docs/tutorials.md`, `docs/reference.md` | document the new API (modify) | 4 |
| `tests/integration/test_batch.py` | round-trip against the real API (create) | 5 |

---

### Task 1: The multipart encoder and decoder

Pure functions over bytes. No httpx, no models, no settings. This is the only part of the
feature with fiddly format details, and it is fully testable without a network.

**Files:**
- Create: `src/edutap/wallet_google/multipart.py`
- Create: `tests/test_multipart.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `SubRequest` — dataclass with `method: str`, `path: str`, `body: str | None`,
    `content_id: str`.
  - `SubResponse` — dataclass with `content_id: str | None`, `status_code: int`,
    `body: dict | None`.
  - `encode_multipart(sub_requests: list[SubRequest], boundary: str) -> bytes`
  - `decode_multipart(content: bytes, content_type: str) -> list[SubResponse]`
  - `make_boundary() -> str`

**Format note, read before implementing.** Google's Wallet examples show each part with
`Content-Type: application/json` followed by the request line. Google's general batch
protocol uses `Content-Type: application/http` for the parts. The Wallet pages are what we
have, so encode as they show, and keep the part content type in the module-level constant
`_PART_CONTENT_TYPE` so switching it is a one-line change. Task 5 settles which one the
server actually accepts.

- [ ] **Step 1: Write the failing encoder test**

Create `tests/test_multipart.py`:

```python
"""Tests for multipart/mixed encoding and decoding."""

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
```

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_multipart.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'edutap.wallet_google.multipart'`

- [ ] **Step 3: Write the encoder**

Create `src/edutap/wallet_google/multipart.py`:

```python
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


def encode_multipart(sub_requests: list[SubRequest], boundary: str) -> bytes:
    """Encode sub-requests as a ``multipart/mixed`` body.

    :param sub_requests: The requests to carry, in order.
    :param boundary:     Delimiter between the parts, without leading dashes.
    :return:             The encoded body, ready to be sent as request content.
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

Run: `uv run pytest tests/test_multipart.py -v`
Expected: PASS

- [ ] **Step 5: Write the failing decoder tests**

Append to `tests/test_multipart.py` — but put the new import in the **top-of-file import
block** beside the existing ones, not here. Ruff's `E402` is active in this project
(`select = ["E", "F", "W", "I", "UP"]`, only `E501` ignored), so a mid-file import fails
`tox -e lint`.

```python
# this import belongs at the top of the file, with the others
from edutap.wallet_google.multipart import decode_multipart


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
    # `body` is typed `dict | None`; the project's ty hook raises
    # not-subscriptable without this narrowing.
    assert responses[1].body is not None
    assert responses[1].body["error"]["code"] == 404


def test_decode_strips_the_response_prefix_from_content_id():
    """Google echoes Content-ID with a 'response-' prefix; we map back to ours."""
    responses = decode_multipart(
        MULTIPART_RESPONSE.encode("utf-8"),
        "multipart/mixed; boundary=rspboundary",
    )

    assert [r.content_id for r in responses] == ["item-0", "item-1"]
```

- [ ] **Step 6: Run them and watch them fail**

Run: `uv run pytest tests/test_multipart.py -v`
Expected: FAIL — `ImportError: cannot import name 'decode_multipart'`

- [ ] **Step 7: Write the decoder**

Append to `src/edutap/wallet_google/multipart.py`:

```python
def _parse_http_payload(payload: str) -> tuple[int, dict | None]:
    """Parse an embedded HTTP response into status code and JSON body.

    :param payload: A raw HTTP response: status line, headers, blank line, body.
    :return:        Tuple of status code and decoded body (None when not JSON).
    """
    head, _, body = payload.partition(f"{_CRLF}{_CRLF}")
    status_line = head.split(_CRLF, 1)[0]
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
        return status_code, json.loads(body)
    except json.JSONDecodeError:
        return status_code, None


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
```

- [ ] **Step 8: Run the whole file**

Run: `uv run pytest tests/test_multipart.py -v`
Expected: PASS, 4 tests

The fourth is `test_decode_returns_status_code_zero_for_malformed_status_line`, added
during review: a part whose status line cannot be parsed must come back as a
`SubResponse` with `status_code=0` rather than raising out of `decode_multipart`. It
exists because the `try`/`except` above was missing from the first draft of this plan,
and one malformed part would have destroyed every other result in the same response —
against this feature's core commitment that partial failures come back as results. Note
for anyone naming tests here: `codespell` runs in `tox -e lint` and rejects the
adjective formed from "un" + "parseable" — use "malformed" instead. (Spelling it out
would fail this very file, as an earlier revision of this plan discovered.)

- [ ] **Step 9: Lint and commit**

```bash
uvx ruff format src/edutap/wallet_google/multipart.py tests/test_multipart.py
uvx ruff check src/edutap/wallet_google/multipart.py tests/test_multipart.py
git add src/edutap/wallet_google/multipart.py tests/test_multipart.py
git commit -m "feat(batch): add multipart/mixed encoder and decoder"
```

---

### Task 2: The `Batch` class and `execute()`

**Files:**
- Create: `src/edutap/wallet_google/batch.py`
- Create: `tests/test_batch.py`
- Modify: `src/edutap/wallet_google/settings.py`
- Modify: `src/edutap/wallet_google/api.py`

**Interfaces:**
- Consumes: `SubRequest`, `SubResponse`, `encode_multipart`, `decode_multipart`,
  `make_boundary` from Task 1.
- Produces:
  - `BatchError` — Pydantic model with `code: int`, `message: str`, `status: str | None`.
  - `BatchResult` — Pydantic model with `index: int`, `name: str`, `resource_id: str`,
    `status_code: int`, `body: dict | None`, `error: BatchError | None`, and a property
    `ok: bool`.
  - `Batch` — class with `add_update(name, data)`, `add_updates(name, data_list)`,
    `__len__()`, and `execute(*, credentials=None) -> list[BatchResult]`.
  - `settings.batch_url`
  - `api.Batch` — re-export, so `api.Batch()` works alongside `api.read()` etc.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_batch.py`:

```python
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
    assert results[0].body["id"] == "issuer.one"
    assert results[1].body["id"] == "issuer.two"
```

- [ ] **Step 2: Run and watch them fail**

Run: `uv run pytest tests/test_batch.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'edutap.wallet_google.batch'`

- [ ] **Step 3: Add the settings entry**

In `src/edutap/wallet_google/settings.py`, beside `API_URL`:

```python
BATCH_URL = "https://walletobjects.googleapis.com/batch"
```

and in the `Settings` class, beside `api_url`:

```python
    batch_url: AnyHttpUrl = AnyHttpUrl(BATCH_URL)
```

It is deliberately *not* derived from `api_url`: the batch endpoint sits one level above
`/walletobjects/v1`, so appending would produce the wrong URL.

- [ ] **Step 4: Write the `Batch` class**

Create `src/edutap/wallet_google/batch.py`:

```python
"""Batch requests against the Google Wallet API.

A :class:`Batch` collects sub-requests and sends them as a single
``multipart/mixed`` request. One Batch is one HTTP request — which is the point:
the Google Wallet API is rate limited per call, so a hundred updates in one
Batch cost what one update costs.

See https://developers.google.com/wallet/generic/resources/performance-tips
"""

from .clientpool import client_pool
from .models.bases import make_partial_model
from .models.bases import Model
from .multipart import decode_multipart
from .multipart import encode_multipart
from .multipart import make_boundary
from .multipart import SubRequest
from .multipart import SubResponse
from .registry import lookup_metadata_by_name
from .registry import raise_when_operation_not_allowed
from .utils import handle_response_errors
from pydantic import ValidationError as PydanticValidationError

import typing
import urllib.parse


class BatchError(Model):
    """The error Google reports for a single failed sub-request."""

    code: int
    message: str
    status: str | None = None


class BatchResult(Model):
    """The outcome of one sub-request, correlated back to its input item."""

    index: int
    name: str
    resource_id: str
    status_code: int
    body: dict | None = None
    error: BatchError | None = None

    @property
    def ok(self) -> bool:
        """True when Google accepted this sub-request."""
        return self.error is None and 200 <= self.status_code < 300


class Batch:
    """Collects sub-requests and sends them as one API call.

    Fill it, then execute it::

        batch = Batch()
        batch.add_update("LoyaltyObject", {"id": "issuer.m1", "state": "EXPIRED"})
        results = batch.execute()

    Pass types may be mixed freely — each sub-request carries its own path.
    """

    def __init__(self) -> None:
        self._sub_requests: list[SubRequest] = []
        # Parallel to _sub_requests: what each one was about, for the results.
        self._items: list[tuple[str, str]] = []

    def __len__(self) -> int:
        """Number of sub-requests collected so far.

        One Batch is one HTTP request, so this is the number the caller needs in
        order to decide whether to send it or start a new one.
        """
        return len(self._sub_requests)

    def add_update(self, name: str, data: dict[str, typing.Any]) -> None:
        """Add a PATCH for one object.

        Only the attributes present in ``data`` are sent. The payload is
        validated here rather than at execute time, so a typo fails on the line
        that caused it.

        :param name: Registered model name, e.g. "LoyaltyObject".
        :param data: The attributes to change, plus the resource id.
        :raises ValueError: When the payload is invalid or carries no resource id.
        """
        metadata = lookup_metadata_by_name(name)
        raise_when_operation_not_allowed(name, "update")
        resource_id_key = metadata["resource_id"]

        resource_id = data.get(resource_id_key)
        if not resource_id:
            raise ValueError(
                f"Item for '{name}' has no '{resource_id_key}'; nothing to update."
            )

        partial_model = make_partial_model(metadata["model"])
        try:
            verified = partial_model.model_validate(data)
        except PydanticValidationError as exc:
            raise ValueError(f"Item '{resource_id}' is invalid for '{name}': {exc}") from exc

        api_path = urllib.parse.urlparse(str(client_pool.settings.api_url)).path
        self._sub_requests.append(
            SubRequest(
                method="PATCH",
                path=f"{api_path}/{metadata['url_part']}/{resource_id}",
                body=verified.model_dump_json(exclude_unset=True, by_alias=True),
                content_id=f"item-{len(self._sub_requests)}",
            )
        )
        self._items.append((name, resource_id))

    def add_updates(
        self,
        name: str,
        data: list[dict[str, typing.Any]],
    ) -> None:
        """Add a PATCH for each object in a list.

        :param name: Registered model name, applied to every item.
        :param data: One dict per object.
        :raises ValueError: When any payload is invalid or carries no resource id.
        """
        for item in data:
            self.add_update(name, item)

    def _ordered_sub_requests(self) -> list[SubRequest]:
        """Return the sub-requests in the order they should go on the wire.

        Grouped by pass type. ``sorted`` is stable, so within a type the add
        order survives. This is free to change: results are correlated by
        Content-ID, not by position, so reordering here cannot affect what
        :meth:`execute` returns.
        """
        order = sorted(
            range(len(self._sub_requests)),
            key=lambda index: self._items[index][0],
        )
        return [self._sub_requests[index] for index in order]

    def _build_results(self, sub_responses: list[SubResponse]) -> list[BatchResult]:
        """Correlate sub-responses back to the items that produced them.

        Correlation is by Content-ID, not by position: the specification does not
        promise the server answers in the order it was asked.
        """
        by_content_id = {r.content_id: r for r in sub_responses if r.content_id}
        results: list[BatchResult] = []
        for index, (name, resource_id) in enumerate(self._items):
            sub_response = by_content_id.get(f"item-{index}")
            if sub_response is None:
                results.append(
                    BatchResult(
                        index=index,
                        name=name,
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
                    name=name,
                    resource_id=resource_id,
                    status_code=sub_response.status_code,
                    body=body,
                    error=error,
                )
            )
        return results

    def execute(self, *, credentials: dict | None = None) -> list[BatchResult]:
        """Send the collected sub-requests as one API call.

        Individual sub-request failures do **not** raise; they come back as
        results carrying an ``error``. Only the batch request itself failing
        raises.

        Sub-requests may be grouped and reordered on the wire. The results are
        not: they come back in the order the items were added, correlated by
        Content-ID.

        This does not chunk, throttle or retry. The Google Wallet API is rate
        limited to 20 calls per second; staying within it is the caller's
        business. Parameters are keyword-only so that a later driver stage can
        add ``chunk_size`` and friends without breaking existing calls.

        :param credentials: Optional session credentials as dict.
        :raises WalletException: When the batch request itself fails.
        :return: One result per added sub-request, in the order they were added.
        """
        if not self._sub_requests:
            return []
        boundary = make_boundary()

        client = client_pool.client(credentials=credentials)
        response = client.post(
            url=str(client_pool.settings.batch_url),
            content=encode_multipart(self._ordered_sub_requests(), boundary),
            headers={"Content-Type": f"multipart/mixed; boundary={boundary}"},
        )
        handle_response_errors(response, "batch", "Batch", f"{len(self)} items")

        return self._build_results(
            decode_multipart(response.content, response.headers.get("Content-Type", ""))
        )
```

- [ ] **Step 5: Re-export from `api.py`**

So that `Batch` sits beside the other public entry points. Add the import:

```python
from .batch import Batch
from .batch import BatchError
from .batch import BatchResult
```

and add `"Batch"`, `"BatchError"` and `"BatchResult"` to `__all__`.

- [ ] **Step 6: Run and watch them pass**

Run: `uv run pytest tests/test_batch.py -v`
Expected: PASS, 10 tests

- [ ] **Step 7: Run the whole suite for regressions**

Run: `uvx tox -e py313`
Expected: PASS

- [ ] **Step 8: Lint and commit**

```bash
uvx ruff format src tests
uvx ruff check src tests
git add src/edutap/wallet_google/batch.py src/edutap/wallet_google/settings.py src/edutap/wallet_google/api.py tests/test_batch.py
git commit -m "feat(batch): add Batch with add_update() and execute()"
```

---

### Task 3: `aexecute()` — the asynchronous twin

**Files:**
- Modify: `src/edutap/wallet_google/batch.py`
- Create: `tests/test_batch_async.py`

**Interfaces:**
- Consumes: `Batch`, `BatchResult` from Task 2.
- Produces: `Batch.aexecute(*, credentials: dict | None = None) -> list[BatchResult]`

Building a Batch has no I/O, so only execution needs an async variant. `add_update()` is
shared between both.

- [ ] **Step 1: Write the failing test**

Create `tests/test_batch_async.py`, repeating the `MULTIPART_RESPONSE` constant from
`tests/test_batch.py` verbatim — the two files are read independently — then:

```python
"""Tests for Batch.aexecute()."""

from edutap.wallet_google.batch import Batch
from edutap.wallet_google.settings import Settings

import httpx
import pytest
import respx


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
```

The marker is `@pytest.mark.asyncio`, matching every async test in
`tests/test_api_async.py`. The repository uses `pytest-asyncio`, not `anyio` — do not
introduce a second convention here.

- [ ] **Step 2: Run and watch it fail**

Run: `uv run pytest tests/test_batch_async.py -v`
Expected: FAIL — `AttributeError: 'Batch' object has no attribute 'aexecute'`

- [ ] **Step 3: Implement it**

Add to the `Batch` class in `src/edutap/wallet_google/batch.py`, directly after
`execute()`:

```python
    async def aexecute(self, *, credentials: dict | None = None) -> list[BatchResult]:
        """Asynchronously send the collected sub-requests as one API call.

        See :meth:`execute` for the full description; behaviour is identical.

        :param credentials: Optional session credentials as dict.
        :raises WalletException: When the batch request itself fails.
        :return: One result per added sub-request, in the order they were added.
        """
        if not self._sub_requests:
            return []
        boundary = make_boundary()

        client = client_pool.async_client(credentials=credentials)
        response = await client.post(
            url=str(client_pool.settings.batch_url),
            content=encode_multipart(self._ordered_sub_requests(), boundary),
            headers={"Content-Type": f"multipart/mixed; boundary={boundary}"},
        )
        handle_response_errors(response, "batch", "Batch", f"{len(self)} items")

        return self._build_results(
            decode_multipart(response.content, response.headers.get("Content-Type", ""))
        )
```

- [ ] **Step 4: Run and watch it pass**

Run: `uv run pytest tests/test_batch_async.py -v`
Expected: PASS, 2 tests

- [ ] **Step 5: Commit**

```bash
uvx ruff format src tests
uvx ruff check src tests
git add src/edutap/wallet_google/batch.py tests/test_batch_async.py
git commit -m "feat(batch): add Batch.aexecute()"
```

---

### Task 4: Prove it across every pass type, and document it

The claim "works for all pass types" is currently an argument about the registry. This
task turns it into a test, and writes the docs.

**Files:**
- Modify: `tests/test_batch.py`
- Modify: `docs/tutorials.md`
- Modify: `docs/reference.md`

**Interfaces:**
- Consumes: `Batch` from Task 2.
- Produces: no new code interfaces.

- [ ] **Step 1: Write the parametrised failing test**

Append to `tests/test_batch.py`:

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
def test_batch_builds_the_right_path_for_every_pass_type(mock_session, name, url_part):
    """The sub-request path comes from the registry, so every type works."""
    route = _mock_batch_endpoint()

    batch = Batch()
    batch.add_update(name, {"id": "issuer.one", "state": "EXPIRED"})
    batch.execute()

    body = route.calls.last.request.content.decode("utf-8")
    assert f"PATCH /walletobjects/v1/{url_part}/issuer.one" in body
```

- [ ] **Step 2: Run it**

Run: `uv run pytest tests/test_batch.py -k every_pass_type -v`
Expected: PASS for all seven. If a type fails because `state` is not one of its fields,
replace the payload for that type with an attribute it does have — do not weaken the
assertion on the path.

- [ ] **Step 3: Document it in the tutorial**

Add a section to `docs/tutorials.md`, after the update section:

````markdown
## Updating many passes at once

A `Batch` collects updates and sends them as a single API call. Because the Google Wallet
API is rate limited per call, a hundred updates in one batch cost what one update costs:

```python
from edutap.wallet_google import api

batch = api.Batch()
batch.add_update("LoyaltyObject", {"id": "issuer.member-1", "state": "EXPIRED"})
batch.add_update("LoyaltyObject", {"id": "issuer.member-2", "state": "EXPIRED"})
results = batch.execute()

for result in results:
    if not result.ok:
        print(f"{result.resource_id} failed: {result.error.message}")
```

Only the attributes you set are sent, so a batch of small changes stays small on the wire.

Pass types may be mixed in one batch — each sub-request carries its own path:

```python
batch = api.Batch()
batch.add_update("LoyaltyObject", {"id": "issuer.member-1", "state": "EXPIRED"})
batch.add_update("EventTicketObject", {"id": "issuer.ticket-9", "state": "COMPLETED"})
```

For the bulk case, add a whole list at once and use `len(batch)` to decide how much goes
into one call:

```python
batch = api.Batch()
batch.add_updates("LoyaltyObject", changed_members)
print(f"sending {len(batch)} updates as one request")
results = batch.execute()
```

A batch is **not** atomic: individual items can fail while the rest succeed, which is why
failures come back as results rather than exceptions. There is one result per added
sub-request, **in the order they were added** — the batch may group and reorder the
sub-requests internally, but that never shows in the results.

`execute()` does not split, throttle or retry. The Google Wallet API is rate limited to 20
calls per second; deciding how many objects go into one batch, and how fast batches follow
each other, is yours.

The asynchronous twin is `await batch.aexecute()` and behaves identically.
````

- [ ] **Step 4: Add the class to the reference**

Add `Batch`, `BatchResult` and `BatchError` to `docs/reference.md`, following whatever
structure the surrounding entries use.

- [ ] **Step 5: Check the Markdown renders**

There is **no** documentation build in this repository — `docs/` holds plain Markdown and
is built centrally for docs.edutap.eu. So there is no `tox -e docs` to run. Instead, read
the two files back and check the fenced code blocks are balanced and the headings sit at
the same level as their neighbours.

- [ ] **Step 6: Commit**

```bash
git add tests/test_batch.py docs/tutorials.md docs/reference.md
git commit -m "docs(batch): document Batch and cover all pass types"
```

---

### Task 5: The integration test, and the measurements

Task 1 encodes the parts as `Content-Type: application/json` because that is what Google's
Wallet examples show, while Google's general batch protocol uses `application/http`. Only
the real endpoint can say which it accepts. This task also produces the two numbers nobody
has: whether a batch counts as one call, and how many sub-requests fit.

**Files:**
- Create: `tests/integration/test_batch.py`
- Modify: `superpowers/plans/2026-08-17-batch-update.md` (this file, Step 6)

**Interfaces:**
- Consumes: `Batch` from Task 2.
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

If it fails with a 400 on the format, switch `_PART_CONTENT_TYPE` in `multipart.py` to
`"application/http"` and — because that content type means each part carries a full HTTP
message — the request line then needs an HTTP version suffix (`PATCH <path> HTTP/1.1`) and
its own `Content-Type: application/json` header before the body. Adjust the Task 1 tests
to match, then re-run.

- [ ] **Step 4: Confirm the one-call assumption in the Cloud Console**

This step needs a human with console access; an agent cannot do it.

The whole design rests on a batch counting as **one** call against the 20/s limit, and
that is an operational finding rather than something Google documents. The console can
turn it into something read off a graph:

1. Note the current request count for `walletobjects.googleapis.com` under
   **APIs & Services → Google Wallet API → Metrics**.
2. Send exactly one batch carrying a known number of sub-requests — 100 is a good size:
   large enough that the two outcomes cannot be confused, small enough to be harmless.
3. Wait for the graph to catch up, then read the increment. **+1 confirms the assumption;
   +100 refutes it** and means this feature buys connection overhead only, at which point
   parallel `aupdate()` calls deserve reconsideration.

While in the console, also check **Quotas & System Limits** for the name and value of the
quota metric that actually governs this API, and whether a separate batch quota exists.

- [ ] **Step 5: Measure the ceiling**

Still in the integration environment, not as a committed test: execute batches with
growing sizes (50, 200, 500, 1000) and record where they start failing, and with what
error.

- [ ] **Step 6: Write the measurements down**

Add a short section to this plan file recording, dated and labelled **measured** — what
the endpoint did on the day we looked, not what Google guarantees:

- the console increment from Step 4 (+1 or +N) and therefore whether the one-call finding
  holds;
- the name and value of the governing quota metric;
- the sub-request count at which batches start failing, and the error.

Anyone sizing a batch later needs to know which of these are measured and which are
documented. As of this writing, none of them is documented.

- [ ] **Step 7: Commit**

```bash
git add tests/integration/test_batch.py superpowers/plans/2026-08-17-batch-update.md
git commit -m "test(batch): add integration round-trip and record measured limits"
```

---

## Verification

- [ ] `uvx tox -e py313` green.
- [ ] `uvx tox -e lint` green.
- [ ] Integration test green against the real API.
- [ ] The Cloud Console increment confirms a batch counts as one call.
- [ ] The measured sub-request ceiling is recorded in this file, labelled as measured.

## Deliberately out of scope

Each of these is a plausible next stage, and none belongs in this one:

- **The driver.** Chunking, throttling to 20 calls/s, retry, resume and progress
  reporting. It arrives as keyword arguments to `execute()` — `chunk_size=None` keeps
  today's meaning of one request, a set value splits transparently — so nothing in this
  plan has to be undone to get there. This is where a daily 70,000-object reconciliation
  actually gets decided, and it wants its own design once the measured ceiling is known.
- **`add_create()` and other operations.** `SubRequest` already carries the method, and
  `Batch` already mixes types, so adding create is a method on the existing class.
- **Parsing results into models.** `BatchResult.body` stays a dict; adding a parsed model
  later does not break the signature.
- **Delta detection.** Writing only genuinely changed objects would cut the daily volume
  far more than batching does, but it belongs in the calling system, not in this library.
