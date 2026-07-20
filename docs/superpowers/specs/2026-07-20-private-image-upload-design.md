# Design: Private Image Upload

Date: 2026-07-20
Status: approved, ready for implementation planning

## Problem

Google Wallet supports *secure private images*: an issuer uploads image bytes to
Google, receives an opaque `privateImageId`, and references that id from
`Image.privateImageId` inside a pass object. Unlike the regular
`Image.sourceUri.uri` mechanism, the image is never served from a publicly
reachable URL.

`edutap.wallet_google` already carries the `privateImageId` field on the `Image`
model (`models/datatypes/general.py`), but offers no way to obtain such an id.
The upload endpoint is therefore unusable through this library today.

The endpoint is absent from the Google Wallet discovery document, has no REST
reference page, and consequently is missing from every generated Google client
library. It is documented only through a Java code sample on the
*secure private images* use-case pages. Implementing it means writing the HTTP
call by hand.

Reference documentation:

- <https://developers.google.com/wallet/generic/use-cases/secure-private-images>
- <https://developers.google.com/wallet/retail/loyalty-cards/use-cases/secure-private-images>
- <https://developers.google.com/wallet/tickets/boarding-passes/use-cases/secure-private-images>

## Endpoint contract

```
POST https://walletobjects.googleapis.com/upload/walletobjects/v1/privateContent/{issuerId}/uploadPrivateImage
Authorization: Bearer <service account token, scope wallet_object.issuer>
Content-Type: <image mime type>

<raw image bytes>
```

Response body:

```json
{"privateImageId": "..."}
```

Notes taken from the documentation:

- Simple upload with a raw body. No `uploadType` query parameter, no multipart
  and no resumable protocol is documented.
- The path parameter is the **issuer id**, not a resource id.
- The request schema `UploadPrivateImageRequest` exists in the discovery
  document but has no properties, which matches a pure media body.
- Google documents **no** size, format or quota limits for this endpoint.

Constraints imposed by Google on the resulting id:

- Usable on wallet **objects** only, never on classes.
- Usable only in `imageModulesData[].mainImage` — not for logo,
  `wideHeaderLogo` or `heroImage`.
- Each uploaded image may be referenced by exactly **one** object. There is no
  reuse across passes, and no delete operation.
- Not combinable with Generic Private Passes.
- Gated: the `Image.privateImageId` field documentation states
  "Please contact support to use private images." Issuers that are not on the
  allowlist will be rejected by the server.

## Scope

In scope: the upload operation and its integration with the existing
`ImageProvider` plugin system, plus tests and documentation.

Out of scope, tracked separately (see *Related gaps* below): every other
Wallet API capability the library is currently missing.

## Public API

Four functions in `edutap.wallet_google.api`, following the established naming
convention (async variants prefixed with `a`):

```python
def upload_private_image(
    data: bytes | ImageData,
    mime_type: str | None = None,
    *,
    issuer_id: str | None = None,
    credentials: dict | None = None,
) -> str: ...


async def aupload_private_image(
    data: bytes | ImageData,
    mime_type: str | None = None,
    *,
    issuer_id: str | None = None,
    credentials: dict | None = None,
) -> str: ...


def upload_private_image_by_id(
    image_id: str,
    *,
    issuer_id: str | None = None,
    credentials: dict | None = None,
) -> str: ...


async def aupload_private_image_by_id(
    image_id: str,
    *,
    issuer_id: str | None = None,
    credentials: dict | None = None,
) -> str: ...
```

All four are exported through `api.__all__`.

### Return value

The bare `privateImageId` string. That value is exactly what belongs into
`Image.privateImageId`; wrapping it in a single-field model would only force
callers to unwrap it again. The response model exists but stays internal.

### Argument handling

`data` accepts two forms:

- `bytes` — `mime_type` is then required. Passing `None` raises `ValueError`.
- `ImageData` (`models.handlers.ImageData`, the type returned by
  `ImageProvider.image_by_id`) — `mime_type` must be `None`, otherwise
  `ValueError`. The mime type is taken from `ImageData.mimetype`.

Paths and file-like objects are deliberately not accepted; callers read the
bytes themselves.

`issuer_id` falls back to the new `Settings.issuer_id`. When neither is set, a
`ValueError` is raised.

`credentials` is passed to the client pool exactly like in every other API
function.

### Usage

```python
from edutap.wallet_google import api

private_image_id = api.upload_private_image(
    image_bytes,
    "image/jpeg",
    issuer_id="3388000000012345",
)

student_pass = api.new(
    "GenericObject",
    {
        "id": "3388000000012345.student-42",
        "classId": "3388000000012345.campus-card",
        "state": "ACTIVE",
        "imageModulesData": [
            {
                "id": "portrait",
                "mainImage": {"privateImageId": private_image_id},
            },
        ],
    },
)
api.create(student_pass)
```

No higher-level helper attaches the id to a model or patches an object. Since
Google permits one image per object, an `upload + patch` helper would either
have to guess which `imageModulesData` entry is meant, or leave an orphaned,
undeletable image behind when the patch fails.

## Architecture

### Module layout

| File | Change |
| --- | --- |
| `models/datatypes/private_content.py` (new) | `UploadPrivateImageResponse` |
| `_private_content.py` (new, internal) | validation, URL building, response parsing |
| `clientpool.py` | `upload_url()` |
| `settings.py` | four new settings fields |
| `api.py` | the four public functions |
| `utils.py` | error handling usable without a registered model name |

`api.py` is already 924 lines long. Putting the validation and URL logic there
would grow it further, so the public functions stay thin wrappers over
`_private_content.py`, mirroring how `create()` and `read()` delegate to their
`_prepare_*` helpers today.

### Transport

The upload does not use `settings.api_url` (`.../walletobjects/v1`) but a
different path prefix (`.../upload/walletobjects/v1`). `client_pool.url()` is
registry-driven and cannot produce it.

`ClientPoolManager` gains:

```python
def upload_url(self, path: str) -> str:
    """Build a URL below the media upload prefix.

    :param path: Path below the API version, must start with a forward slash.
    """
```

It derives the prefix from `settings.upload_api_url`, which defaults to
`https://walletobjects.googleapis.com/upload/walletobjects/v1`.

The HTTP call reuses the **already pooled** `AssertionClient` /
`AsyncAssertionClient` from `client_pool.client()` / `client_pool.async_client()`.
Same token, same connection pool, same credentials semantics as every other
call. No second client type is introduced.

### Settings

```python
upload_api_url: AnyHttpUrl = AnyHttpUrl(UPLOAD_API_URL)
issuer_id: str = ""
private_image_max_bytes: int = 5 * 1024 * 1024
private_image_allowed_mime_types: list[str] = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
]
```

Environment variables follow the existing `EDUTAP_WALLET_GOOGLE_` prefix.

Adding `issuer_id` also closes an existing inconsistency: the docstring of
`api.listing()` already promises a fallback to
`EDUTAP_WALLET_GOOGLE_ISSUER_ID`, but `Settings` only knows `test_issuer_id`,
so that fallback never existed in code. Wiring `listing()`/`alisting()` to the
new field is part of this work.

### Validation

Google documents no limits, so the guardrails are conservative and
configurable rather than guessed and hard-coded:

- `mime_type` must be in `private_image_allowed_mime_types` — the list is
  derived from the image formats the Wallet image guidelines accept, and is
  overridable.
- `len(data)` must not exceed `private_image_max_bytes`. A value of `0`
  disables the check. The default of 5 MB mirrors the only documented media
  upload limit in the Wallet API (rotating barcode values).
- No magic-byte sniffing. It would require a new dependency or hand-maintained
  signature tables for little gain.

Violations raise `ValueError` before any HTTP request is made, so no request is
burned against the 20 requests/second rate limit.

### Data flow

```
bytes | ImageData
  -> normalise to (data: bytes, mime_type: str)
  -> mime_type in allowed list?            no -> ValueError
  -> len(data) <= max_bytes (if max > 0)?  no -> ValueError
  -> issuer_id or settings.issuer_id       empty -> ValueError
  -> POST client_pool.upload_url(
         f"/privateContent/{issuer_id}/uploadPrivateImage")
     Content-Type: {mime_type}, body: raw bytes
  -> handle_response_errors(...)
  -> UploadPrivateImageResponse.model_validate_json(...).privateImageId
```

The `_by_id` variants prepend: `get_image_providers()`, require exactly one
provider (more than one is an error, matching the behaviour of
`handlers.fastapi.handle_image`), then `await provider.image_by_id(image_id)`
to obtain an `ImageData`.

### Synchronous bridge to the async plugin

`ImageProvider.image_by_id` is async by protocol. `upload_private_image_by_id`
bridges with `asyncio.run()`.

Before doing so it calls `asyncio.get_running_loop()`. If a loop is already
running — the FastAPI case — it raises `RuntimeError` pointing at
`aupload_private_image_by_id`, instead of deadlocking silently.

## Error handling

`handle_response_errors()` from `utils.py` is reused, keeping the existing
taxonomy intact:

| Condition | Exception |
| --- | --- |
| 403 with quota/rate keywords | `QuotaExceededException` |
| 404 | `LookupError` |
| other non-2xx | `WalletException` |
| client-side validation | `ValueError` |
| sync `_by_id` inside a running loop | `RuntimeError` |

`handle_response_errors()` currently expects a registered model name for its
message. It is extended to accept a plain operation context so the private
image call can produce a readable message without inventing a fake model name.

Because the feature is allowlist-gated, a non-allowlisted issuer is a
*likely* failure mode, not an exotic one. The error message for 403 and 404 on
this endpoint must state explicitly that private images require Google support
to enable them for the issuer. Without that hint the failure is very hard to
diagnose.

## Testing

Test-driven: tests are written before the implementation. The endpoint
behaviour is modelled after the Java sample in Google's documentation.

### Unit tests — `tests/test_api_private_image.py`

Mocked with `respx`, following the pattern of `test_api_sync.py` and
`test_api_async.py`.

- successful upload, sync and async, returns the `privateImageId`
- request assertions: URL contains the issuer id, `Content-Type` equals the
  supplied mime type, body equals the supplied bytes
- `ImageData` input takes its mime type from the model
- `bytes` without `mime_type` -> `ValueError`
- `ImageData` together with `mime_type` -> `ValueError`
- disallowed mime type -> `ValueError`
- payload larger than `private_image_max_bytes` -> `ValueError`
- `private_image_max_bytes = 0` disables the size check
- no `issuer_id` and empty `Settings.issuer_id` -> `ValueError`
- `issuer_id` falls back to `Settings.issuer_id`
- 403 quota -> `QuotaExceededException`; 404 -> `LookupError`;
  500 -> `WalletException`
- `_by_id` with the fake provider from
  `tests/data/test_wallet_google_plugins/`, sync and async
- `_by_id` with zero or multiple registered providers -> error
- sync `_by_id` called from inside a running event loop -> `RuntimeError`

### Integration test — `tests/integration/test_private_image.py`

Marked `@pytest.mark.integration`. Uploads a small real PNG and uses the
returned id in a `GenericObject`.

This test will fail for issuers that are not allowlisted, which is the normal
state. It is therefore additionally gated behind
`EDUTAP_WALLET_GOOGLE_TEST_PRIVATE_IMAGES=1` and skipped otherwise, so that
`--run-integration` stays green for everyone else.

## Documentation

Following the Diátaxis structure already used in `docs/`:

- `docs/tutorials.md` — how-to: upload an image, place the id in
  `imageModulesData`, create the object.
- `docs/reference.md` — the four function signatures, the new settings fields
  and their defaults.
- `docs/explanation.md` — when to use a private image versus the existing
  `ImageProvider` plugin serving images over a public URL, plus the Google-side
  constraints (objects only, `imageModulesData` only, one image per object,
  no delete, allowlist required).

The allowlist requirement is also mentioned in `README.md`, because a user
hitting a 403 will look there first.

## Explicitly not included

- Caching or reuse of a `privateImageId` — Google forbids referencing one image
  from more than one object.
- Deleting an uploaded image — no such endpoint exists.
- An `attach`/`set` helper that mutates or patches a pass model.
- Private images on hero images or on the web — announced by Google as
  "in development", not available yet.

## Related gaps (out of scope, for later work)

Recorded here so the analysis is not lost. Each needs its own spec:

1. `privateContent.setPassUpdateNotice` — update notifications for Generic
   Private Passes.
2. `media.upload` / `media.download` —
   `uploadRotatingBarcodeValues` / `downloadRotatingBarcodeValues` on
   `transitObject` for partner-generated rotating barcodes. The
   `RotatingBarcode` models exist, the transport does not.
3. `modifyLinkedOfferObjects` on `eventticketobject` and `loyaltyobject`.
4. `jwt.insert` — the `JwtResource` and `JwtResponse` models exist, but
   `api.create()` would validate the response against `JwtResource` instead of
   `JwtResponse`, so the documented path for JWTs longer than 1800 characters
   is not usable.
5. Batch requests against `https://walletobjects.googleapis.com/batch`
   (`multipart/mixed`), relevant for bulk operations under the
   20 requests/second limit.
6. Transport refinements: gzip, ETags, retry with backoff on 429 and quota
   errors.
