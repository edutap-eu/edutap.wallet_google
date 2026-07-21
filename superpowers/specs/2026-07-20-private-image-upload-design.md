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

### Source documentation and its state

The use-case page is the only narrative documentation. It exists as three
content-identical copies, one per vertical (verified 2026-07-20, page last
updated 2026-07-16):

- <https://developers.google.com/wallet/generic/use-cases/secure-private-images>
- <https://developers.google.com/wallet/retail/loyalty-cards/use-cases/secure-private-images>
- <https://developers.google.com/wallet/tickets/boarding-passes/use-cases/secure-private-images>

The REST reference is not a usable source here — it is incomplete:

| Source | `privateImageId` | `uploadPrivateImage` method |
| --- | --- | --- |
| use-case page | described, with the endpoint URL and a Java sample | yes |
| discovery document, rev. 20260717 | present in the `Image` schema, plus `UploadPrivateImageRequest` and `UploadPrivateImageResponse` | absent |
| `reference/rest/v1/Image` | **missing entirely** | page returns 404 |

So the use-case page is authoritative for behaviour, the discovery document is
authoritative for the payload schemas, and no formal documentation of the
method signature exists anywhere.

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
- Possibly gated. The discovery document's description of
  `Image.privateImageId` ends with "Please contact support to use private
  images." The use-case page does not mention any allowlist or onboarding step.
  Whether a non-onboarded issuer is rejected, and with which status code, is
  therefore **unverified** — it has to be established during the integration
  test against a real issuer.

### Server-side error messages

The use-case page documents three concrete error messages. Note that only the
first can occur during the upload itself; the other two are raised when the id
is used on an object, that is during `create()` or `update()`:

| Message | Raised when |
| --- | --- |
| `Image cannot have both source_uri and private_image_id` | an `Image` sets both fields — on object insert/patch |
| `Couldn't find private image with id %s for issuer %s` | a non-existent id is set on an object |
| `Couldn't add private image with id %s for issuer %s to object %s because it is already used with object %s. A private image can only be used with one object.` | the same id is used on a second object; the image must be re-uploaded to obtain a fresh id |

The third message is the server-side enforcement of the one-image-per-object
rule, and it confirms that a hypothetical `upload + patch` convenience helper
would fail *after* the upload had already succeeded — leaving an orphaned,
undeletable image behind. This is the decisive argument against such a helper.

The first message can be prevented client-side: `Image` sets exactly one of
`sourceUri` and `privateImageId`. See *Model validation* below.

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
| `models/datatypes/general.py` | `Image`: validator rejecting `sourceUri` and `privateImageId` together |
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

### Model validation

`Image` currently allows `sourceUri` and `privateImageId` to be set together or
both left unset. Google rejects both cases
("Either this or private_image_id should be set. Requests setting both or
neither will be rejected."), so the failure only surfaces as a server error on
object insert.

`Image` gains a Pydantic model validator enforcing exactly one of the two.
`Image()` with neither field set is currently used in tests and possibly by
consumers as an empty placeholder — the validator therefore rejects only the
"both set" case as an error and leaves "neither set" permitted, matching the
existing lenient `None` defaults throughout the models. This is a deliberate
narrowing: it catches the mistake that is genuinely easy to make (copying a
model and adding `privateImageId` without removing `sourceUri`) without
breaking existing construction patterns.

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

**Added after implementation review:** this bridge creates and tears down a
fresh event loop on *every* call. An `ImageProvider` implementation that caches
an async resource across calls — a module-level `httpx.AsyncClient`, for
instance — binds that resource to the first loop, which is already closed by
the second call. Such an implementation fails on its second use. Providers
meant for the synchronous bridge must create their async resources per call;
otherwise the caller should use `aupload_private_image_by_id`. This constraint
is documented in `docs/explanation.md`; it was not part of the original design
and surfaced during the code review of the bridge.

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

On 403 and 404 from the upload endpoint the message points at the possible
onboarding requirement ("Please contact support to use private images", per the
discovery document) as one candidate cause. Since the gating is unverified, the
wording must stay a hint rather than a diagnosis — but without any hint at all
the failure is very hard to place.

The three server-side messages from the *Server-side error messages* table
above arrive as `WalletException` from `create()`/`update()`, not from the
upload. They need no special handling in code; they belong in the
documentation, so that a reader who hits
`... already used with object %s` knows the fix is a re-upload, not a retry.

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
- `Image(sourceUri=..., privateImageId=...)` -> `ValidationError`
- `Image(privateImageId=...)` and `Image(sourceUri=...)` both validate

### Integration test — `tests/integration/test_private_image.py`

Marked `@pytest.mark.integration`. Uploads a small real PNG and uses the
returned id in a `GenericObject`.

Beyond the happy path it has to answer the questions the documentation leaves
open. These are verification goals, not assertions that can be written blind:

1. **Does an issuer need onboarding?** Establish what a non-onboarded issuer
   receives, and with which status code, so the error message added in
   *Error handling* can be worded from evidence rather than from the discovery
   document's hint.
2. **May one object carry more than one private image?** Upload two images and
   reference both from separate `imageModulesData` entries on the same object.
   The ESC use case depends on this; see the worked example.
3. **How is a private image rendered compared to a `sourceUri` image?** Upload
   a QR code and confirm it is still machine-readable on a device. This step is
   manual — a scanner is required — and is documented as such rather than
   automated.

Gating: the test is additionally hidden behind
`EDUTAP_WALLET_GOOGLE_TEST_PRIVATE_IMAGES=1` and skipped otherwise, so that
`--run-integration` stays green for everyone else. Two reasons: the feature may
require onboarding, and every run leaves permanently undeletable images and
objects behind at Google.

The findings from goals 1 to 3 are written back into this spec and into
`docs/explanation.md` once known. Until then the corresponding statements in
this document are explicitly marked unverified.

## Documentation

Documentation is not an afterthought here. The upload is a one-way,
non-reversible operation whose result the caller is solely responsible for
keeping — a reader who only sees the function signature will get it wrong.
The documentation work is therefore part of the definition of done, following
the Diátaxis structure already used in `docs/`.

### `docs/tutorials.md` — how-to

Upload an image, place the id in `imageModulesData`, create the object. Uses
the European Student Card scenario, because it is the real motivating case
(see *Worked example* below) and because its two private images per pass make
the persistence obligation concrete rather than theoretical.

Second, shorter section: getting the image onto the **front** of the card via
`classTemplateInfo.cardTemplateOverride`. Private images live in
`imageModulesData`, which by default renders in the details view only. The
use-case page shows the Java equivalent; the library already has all the
required models (`ClassTemplateInfo`, `CardTemplateOverride`,
`CardRowTemplateInfo`, `CardRowTwoItems`, `TemplateItem`, `FieldSelector`,
`FieldReference` in `models/datatypes/class_template_info.py`), so this is
purely a documentation gap:

```python
generic_class = api.new(
    "GenericClass",
    {
        "id": f"{issuer_id}.student-id",
        "classTemplateInfo": {
            "cardTemplateOverride": {
                "cardRowTemplateInfos": [
                    {
                        "twoItems": {
                            # these ids must match the object's
                            # textModulesData[].id and imageModulesData[].id
                            "startItem": {
                                "firstValue": {
                                    "fields": [
                                        {"fieldPath": "object.textModulesData['name']"},
                                    ],
                                },
                            },
                            "endItem": {
                                "firstValue": {
                                    "fields": [
                                        {"fieldPath": "object.imageModulesData['photo']"},
                                    ],
                                },
                            },
                        },
                    },
                ],
            },
        },
    },
)
api.create(generic_class)
```

### `docs/reference.md`

The four function signatures, the new settings fields and their defaults, the
`Image` validator, and the table of server-side error messages with the
required remedy for each.

### `docs/explanation.md`

Two sections.

**Private image or `ImageProvider`?** The library already offers a way to serve
images that are not on a CDN: an `ImageProvider` plugin plus the FastAPI
`/images/{encrypted_image_id}` route. That endpoint is reachable by anyone who
has the URL — the id is encrypted, not authenticated. A private image is never
publicly reachable at all. The trade-offs:

| | `ImageProvider` + public route | private image |
| --- | --- | --- |
| reachable without the pass | yes, if the URL leaks | no |
| usable on classes | yes | no |
| usable for logo / hero image | yes | no |
| reusable across passes | yes | no, one image per object |
| changeable after issuing | yes, same URL new bytes | no, requires re-upload and patch |
| requires a reachable service | yes | no |
| caller must persist anything | no | yes, see below |

**Lifecycle and the obligation to persist the id.** This section carries the
warning, because getting it wrong is silent and unrecoverable:

- The id is returned exactly once. Google offers no endpoint to list an
  issuer's private images.
- There is no delete operation.
- An id may be referenced by one object only; a second object needs a fresh
  upload.

Consequences the reader must act on:

1. **Persist the id together with the object it belongs to, before creating the
   object.** If the process dies between upload and `create()`, the id is lost
   and the image is orphaned at Google forever.
2. **Never retry an upload as part of a `create()` retry.** Upload once, then
   retry only the `create()`. A naive retry loop around both leaks one image
   per attempt.
3. **Re-issuing a pass means re-uploading the image.**

The library deliberately stores nothing. Where the mapping lives — a relational
table, a compacted Kafka topic, anything else — is an application decision.
A minimal relational shape for orientation:

```sql
CREATE TABLE private_image (
    object_id        text        NOT NULL,
    module_id        text        NOT NULL,
    source_ref       text        NOT NULL,  -- how the app identifies the source image
    private_image_id text        NOT NULL,
    uploaded_at      timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (object_id, module_id)
);
```

A note on event streams: an "image uploaded" event is useful for auditing, but
an event log is not a lookup store. The source of truth for
"which id belongs to this pass" must be queryable by object id.

### `README.md`

One short paragraph: the feature exists, it may require onboarding with Google
support, and it obliges the caller to persist the returned id. Someone hitting
a 403 looks there first.

## Worked example: European Student Card with two private images

The European Student Card as issued by LMU is the case that motivates the
feature, and the tutorial is written against it. It is richer than a plain
portrait, because it carries **two** person-specific images on the front of the
card.

A note on the source material: `edutap.eugloh_samples` and
`edutap.demo_service` are demonstration repositories. They deliberately take
the shortest path — module-level sample data, images on a public CDN — and are
not a description of how a production issuer should work. The example below
describes the production shape; the demo repositories are cited only because
they show the image layout of a real card.

### The card

Per issued pass, three images appear in `imageModulesData`:

| module id | content | person-specific | rendering |
| --- | --- | --- | --- |
| `photo` | portrait | yes | front, via `cardTemplateOverride` |
| `qr_code` | ESC QR code with the ESC logo, encoding the ESCN | yes | front, own card row |
| `esc` | ESC programme logo | no, identical on every card | details view |

Several portrait crops (square, round, boxed) may be held internally for
different use cases, but exactly **one** of them ends up on the pass. Choosing
the variant happens before the upload; it is not a concern of this library and
does not multiply the number of uploads.

So: **two uploads per issued pass**, one for the portrait and one for the QR
code.

### Why it matters

The QR code is the stronger argument, not the portrait. Its URL is an opaque
UUID, which is obscurity rather than access control, and its payload is the
ESCN — a persistent personal identifier tied to the holder's institution.
A production issuer must not serve the portrait and a personal identifier from
an unauthenticated public origin. Private images remove that origin entirely:
there is no URL to leak.

The programme logo stays a public URL. It is not personal data, it is identical
on every card, and since one private image serves exactly one object, moving it
would mean one upload per issued pass for a constant image.

### The class template needs no change

This is the reassuring part. The `cardTemplateOverride` lives on the **class**
and refers to module ids only:

```python
FieldReference(fieldPath="object.imageModulesData['qr_code']")
```

The private image lives on the **object**. Classes cannot carry private images
at all — and they do not need to. A single shared class template stays valid
for every holder; only the object side changes. That `cardTemplateOverride`
path is also the only way to get a private image onto the front of the card,
since `imageModulesData` otherwise renders in the details view only.

### Before and after

```python
# before: both personal images served from a public CDN
image_data = [
    ImageModuleData(
        id="photo",
        mainImage=Image(sourceUri=ImageUri(uri=f"{CDN}/lmu-ausweise/{name}_box@3x.png")),
    ),
    ImageModuleData(
        id="qr_code",
        mainImage=Image(sourceUri=ImageUri(uri=f"{CDN}/card-{card_uuid}.png")),
    ),
    ImageModuleData(
        id="esc",
        mainImage=Image(sourceUri=ImageUri(uri=f"{CDN}/esc.png")),
    ),
]
```

```python
# after: persist each id immediately after its upload, then create the object
photo_id = api.upload_private_image(portrait_bytes, "image/png")
store.put(object_id, "photo", photo_id)

qr_id = api.upload_private_image(qr_code_bytes, "image/png")
store.put(object_id, "qr_code", qr_id)

image_data = [
    ImageModuleData(id="photo", mainImage=Image(privateImageId=photo_id)),
    ImageModuleData(id="qr_code", mainImage=Image(privateImageId=qr_id)),
    # unchanged: shared, non-personal, one image would serve one object only
    ImageModuleData(
        id="esc",
        mainImage=Image(sourceUri=ImageUri(uri=f"{CDN}/esc.png")),
    ),
]
```

Persisting after **each** upload rather than once before `create()` matters
here: with two uploads the failure surface doubles. If the second upload fails,
the first id must still be recoverable, otherwise that image is orphaned.

This is also why the store is keyed by `(object_id, module_id)` rather than by
object alone — with two private images per pass, an object-keyed schema would
be wrong.

### Lifecycle over an academic year

- Changing the validity period is a `patch` on the same object id. The images
  stay valid and are not re-uploaded.
- Re-issuing the card produces a new object, which needs two new uploads. The
  previous images cannot be transferred and cannot be deleted.

### Open questions this example raises

Both must be answered by the integration test before the ESC use case can be
considered supported. Neither is answered by Google's documentation:

1. **More than one private image per object.** Google states that an image can
   be used with a single object; nothing states how many private images an
   object may carry, and `imageModulesData` is a list. The ESC card requires
   two. Plausible, but unverified — if it does not hold, the use case does not
   work.
2. **Rendering fidelity for functional images.** The QR code is scanned, and it
   carries a logo overlay, which already consumes error-correction headroom.
   Whether Google re-encodes, recompresses or rescales private images
   differently from `sourceUri` images is undocumented. For a portrait a
   quality loss would be cosmetic; here it can break scannability. The test
   must render the pass on a device and read the code with a real scanner, not
   merely assert that the upload returned an id.

A third, operational consequence: because objects cannot be deleted and private
images cannot be deleted either, every integration test run against the real
API leaves two permanent images behind. This reinforces the decision to gate
those tests behind their own environment flag.

## Explicitly not included

- Caching or reuse of a `privateImageId` — Google forbids referencing one image
  from more than one object.
- Deleting an uploaded image — no such endpoint exists.
- An `attach`/`set` helper that mutates or patches a pass model.
- Any persistence of the `privateImageId` — no database schema, no event
  publishing, no plugin protocol for a store. The library stays a pure API
  client, consistent with how it handles callbacks (a protocol the application
  implements) rather than owning state. A `PrivateImageStore` protocol seam
  offering `lookup()`/`store()` for retry idempotency was considered and
  deferred: it should be decided once the demo service has issued real private
  image passes and we know whether the idempotency is needed in practice.
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
