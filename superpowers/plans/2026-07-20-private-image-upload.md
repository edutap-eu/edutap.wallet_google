# Private Image Upload Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the undocumented Google Wallet `uploadPrivateImage` endpoint to `edutap.wallet_google`, so callers can obtain a `privateImageId` for `Image.privateImageId` instead of serving personal images from a public URL.

**Architecture:** Four thin public functions in `api.py` (sync and async, plus an `ImageProvider` plugin bridge for each) delegate to a new internal module `_private_content.py` that does input normalisation, validation and URL building. The HTTP call reuses the existing pooled `AssertionClient`; only the URL prefix differs, which a new `ClientPoolManager.upload_url()` supplies.

**Tech Stack:** Python 3.12+, Pydantic v2, pydantic-settings, httpx + authlib (`AssertionClient` / `AsyncAssertionClient`), pytest + pytest-asyncio + respx, ruff, ty.

**Spec:** `superpowers/specs/2026-07-20-private-image-upload-design.md` — read it before starting. It explains *why* each decision was made; this plan only says *what* to type.

## Global Constraints

- Branch: `feature/private-image-upload`. Never commit to `main`. Never `git push` — the user pushes.
- Conventional Commits. Commit message body in English.
- Code, comments and identifiers in English.
- Endpoint: `POST {upload_api_url}/privateContent/{issuerId}/uploadPrivateImage`, raw image bytes as body, `Content-Type` = the image mime type. Response: `{"privateImageId": "..."}`.
- Upload API URL default: `https://walletobjects.googleapis.com/upload/walletobjects/v1`
- Settings env prefix: `EDUTAP_WALLET_GOOGLE_`
- Default allowed mime types: `image/jpeg`, `image/png`, `image/webp`, `image/gif`
- Default max upload size: `5 * 1024 * 1024` (5 MB); `0` disables the check.
- All models derive from `edutap.wallet_google.models.bases.Model`, which sets `extra="forbid"`.
- Async tests use `@pytest.mark.asyncio`. HTTP is mocked with `respx` plus the `mock_session` / `mock_async_session` fixtures from `tests/conftest.py`.
- Run the test suite with `pytest <path> -v -p no:cacheprovider --no-cov` for fast single-file iteration; the project's `addopts` otherwise force a coverage run.

## File Structure

| File | Responsibility |
| --- | --- |
| `src/edutap/wallet_google/settings.py` | four new configuration fields (modify) |
| `src/edutap/wallet_google/clientpool.py` | `upload_url()` — builds URLs below the media upload prefix (modify) |
| `src/edutap/wallet_google/models/datatypes/private_content.py` | `UploadPrivateImageResponse` (create) |
| `src/edutap/wallet_google/models/datatypes/general.py` | `Image` validator rejecting `sourceUri` + `privateImageId` together (modify) |
| `src/edutap/wallet_google/utils.py` | optional `hint` on `handle_response_errors()` (modify) |
| `src/edutap/wallet_google/_private_content.py` | internal: normalise input, validate, build request, parse response (create) |
| `src/edutap/wallet_google/api.py` | four public functions (modify) |
| `tests/test_api_private_image.py` | unit tests for everything above (create) |
| `tests/integration/test_private_image.py` | gated integration test (create) |
| `docs/tutorials.md`, `docs/reference.md`, `docs/explanation.md`, `README.md` | documentation (modify) |

`_private_content.py` exists so that `api.py` — already 924 lines — only gains thin wrappers, mirroring how `create()` delegates to `_prepare_create()`.

---

### Task 1: Settings and upload URL

**Files:**
- Modify: `src/edutap/wallet_google/settings.py:13-16` (constants), `:35-60` (fields)
- Modify: `src/edutap/wallet_google/clientpool.py:150-162` (next to `url()`)
- Test: `tests/test_api_private_image.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `Settings.upload_api_url: AnyHttpUrl`
  - `Settings.issuer_id: str` (default `""`)
  - `Settings.private_image_max_bytes: int` (default `5242880`)
  - `Settings.private_image_allowed_mime_types: list[str]`
  - `ClientPoolManager.upload_url(path: str) -> str` — `path` must start with `/`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_api_private_image.py`:

```python
"""Tests for the private image upload API."""

from edutap.wallet_google.clientpool import client_pool

import pytest


def test_settings_defaults(mock_settings):
    """The new private image settings have usable defaults.

    `issuer_id` is deliberately not asserted here: `Settings()` reads the
    environment, and a developer with EDUTAP_WALLET_GOOGLE_ISSUER_ID set
    would see a false failure. Its behaviour is covered by the
    resolve_issuer_id tests, which set the value explicitly.
    """
    assert str(mock_settings.upload_api_url) == (
        "https://walletobjects.googleapis.com/upload/walletobjects/v1"
    )
    assert mock_settings.private_image_max_bytes == 5 * 1024 * 1024
    assert "image/jpeg" in mock_settings.private_image_allowed_mime_types
    assert "image/png" in mock_settings.private_image_allowed_mime_types
    assert "image/webp" in mock_settings.private_image_allowed_mime_types
    assert "image/gif" in mock_settings.private_image_allowed_mime_types


def test_upload_url_builds_path(mock_settings):
    """upload_url() appends the path to the upload prefix."""
    url = client_pool.upload_url("/privateContent/123/uploadPrivateImage")

    assert url == (
        "https://walletobjects.googleapis.com/upload/walletobjects/v1"
        "/privateContent/123/uploadPrivateImage"
    )


def test_upload_url_requires_leading_slash(mock_settings):
    """A path without a leading slash is a programming error."""
    with pytest.raises(ValueError, match="forward slash"):
        client_pool.upload_url("privateContent/123/uploadPrivateImage")


def test_upload_url_tolerates_trailing_slash_in_setting(mock_settings):
    """A configured prefix with a trailing slash must not produce a double slash."""
    from pydantic import AnyHttpUrl

    mock_settings.upload_api_url = AnyHttpUrl(
        "https://example.org/upload/walletobjects/v1/"
    )

    url = client_pool.upload_url("/privateContent/123/uploadPrivateImage")

    assert url == (
        "https://example.org/upload/walletobjects/v1"
        "/privateContent/123/uploadPrivateImage"
    )
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_api_private_image.py -v -p no:cacheprovider --no-cov`
Expected: FAIL — `AttributeError: 'Settings' object has no attribute 'upload_api_url'` and `AttributeError: 'ClientPoolManager' object has no attribute 'upload_url'`.

- [ ] **Step 3: Add the settings constants and fields**

In `src/edutap/wallet_google/settings.py`, add the constant below `API_URL`:

```python
API_URL = "https://walletobjects.googleapis.com/walletobjects/v1"
UPLOAD_API_URL = "https://walletobjects.googleapis.com/upload/walletobjects/v1"
SAVE_URL = "https://pay.google.com/gp/v/save"
```

Add the fields directly below `save_url`:

```python
    api_url: AnyHttpUrl = AnyHttpUrl(API_URL)
    upload_api_url: AnyHttpUrl = AnyHttpUrl(UPLOAD_API_URL)
    save_url: AnyHttpUrl = AnyHttpUrl(SAVE_URL)
```

Add the remaining fields directly below `test_issuer_id`:

```python
    test_issuer_id: str = Field(default="")
    issuer_id: str = Field(
        default="",
        description="Default issuer id, used when an API call does not receive one explicitly.",
    )
    private_image_max_bytes: int = Field(
        default=5 * 1024 * 1024,
        description="Maximum accepted size of a private image upload in bytes. 0 disables the check.",
    )
    private_image_allowed_mime_types: list[str] = Field(
        default=[
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif",
        ],
        description="Mime types accepted for private image uploads.",
    )
```

- [ ] **Step 4: Add `upload_url()` to the client pool**

In `src/edutap/wallet_google/clientpool.py`, add directly below the existing `url()` method:

```python
    def upload_url(self, path: str) -> str:
        """
        Create the URL for a media upload endpoint.

        Media uploads do not live below the regular API URL but below a
        separate `/upload` prefix, so this cannot reuse `url()`.

        :param path:        Path below the API version, must start with a
                            forward slash.
        :raises ValueError: When the path does not start with a forward slash.
        :return:            The url of the Google upload endpoint.
        """
        if not path.startswith("/"):
            raise ValueError("path must start with a forward slash")
        prefix = str(self.settings.upload_api_url).rstrip("/")
        return f"{prefix}{path}"
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/test_api_private_image.py -v -p no:cacheprovider --no-cov`
Expected: PASS — 4 passed.

- [ ] **Step 6: Run the full suite to check nothing regressed**

Run: `pytest tests -v -p no:cacheprovider --no-cov -m "not integration"`
Expected: PASS — same number of failures as before your change (ideally zero).

- [ ] **Step 7: Commit**

```bash
git add src/edutap/wallet_google/settings.py src/edutap/wallet_google/clientpool.py tests/test_api_private_image.py
git commit -m "feat: add upload API URL, issuer id and private image settings

Adds Settings.upload_api_url, Settings.issuer_id,
Settings.private_image_max_bytes and
Settings.private_image_allowed_mime_types, plus
ClientPoolManager.upload_url() to build URLs below the /upload prefix,
which the regular registry-driven url() cannot produce."
```

---

### Task 2: Response model and Image validator

**Files:**
- Create: `src/edutap/wallet_google/models/datatypes/private_content.py`
- Modify: `src/edutap/wallet_google/models/datatypes/general.py:58-66` (class `Image`)
- Test: `tests/test_api_private_image.py`

**Interfaces:**
- Consumes: `Settings` from Task 1 (not directly, but the module must import cleanly alongside it).
- Produces:
  - `edutap.wallet_google.models.datatypes.private_content.UploadPrivateImageResponse` with field `privateImageId: str`
  - `Image` raises `pydantic.ValidationError` when `sourceUri` and `privateImageId` are both set.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_api_private_image.py`:

```python
def test_upload_private_image_response_parses():
    """The response model reads the privateImageId out of the JSON body."""
    from edutap.wallet_google.models.datatypes.private_content import (
        UploadPrivateImageResponse,
    )

    response = UploadPrivateImageResponse.model_validate_json(
        '{"privateImageId": "abc123"}'
    )

    assert response.privateImageId == "abc123"


def test_image_accepts_private_image_id_alone():
    """An Image referencing an uploaded private image is valid."""
    from edutap.wallet_google.models.datatypes.general import Image

    image = Image(privateImageId="abc123")

    assert image.privateImageId == "abc123"
    assert image.sourceUri is None


def test_image_accepts_source_uri_alone():
    """The classic public URL form stays valid."""
    from edutap.wallet_google.models.datatypes.general import Image
    from edutap.wallet_google.models.datatypes.general import ImageUri

    image = Image(sourceUri=ImageUri(uri="https://example.org/photo.png"))

    assert image.privateImageId is None


def test_image_accepts_neither():
    """An empty Image stays constructible, it is used as a placeholder."""
    from edutap.wallet_google.models.datatypes.general import Image

    assert Image().sourceUri is None


def test_image_rejects_both_source_uri_and_private_image_id():
    """Google rejects this server side; catch it while building the model."""
    from edutap.wallet_google.models.datatypes.general import Image
    from edutap.wallet_google.models.datatypes.general import ImageUri
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="privateImageId"):
        Image(
            sourceUri=ImageUri(uri="https://example.org/photo.png"),
            privateImageId="abc123",
        )
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_api_private_image.py -v -p no:cacheprovider --no-cov`
Expected: FAIL — `ModuleNotFoundError: No module named 'edutap.wallet_google.models.datatypes.private_content'` and `DID NOT RAISE ValidationError` for the last test.

- [ ] **Step 3: Create the response model**

Create `src/edutap/wallet_google/models/datatypes/private_content.py`:

```python
"""Models for the Google Wallet privateContent endpoints.

The `uploadPrivateImage` method is not part of the Google Wallet discovery
document and has no REST reference page. Both schemas below are taken from the
discovery document, which does contain them:
https://walletobjects.googleapis.com/$discovery/rest?version=v1

See also:
https://developers.google.com/wallet/generic/use-cases/secure-private-images
"""

from ..bases import Model


class UploadPrivateImageResponse(Model):
    """Response of a private image upload.

    The request has no JSON body — the body is the raw image — so only the
    response is modelled here.
    """

    privateImageId: str
```

- [ ] **Step 4: Add the `Image` validator**

In `src/edutap/wallet_google/models/datatypes/general.py`, add the import at the top of the file, next to the other pydantic imports:

```python
from pydantic import model_validator
```

Then replace the body of class `Image` with:

```python
class Image(DeprecatedKindFieldMixin, Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/Image
    """

    # inherits kind (deprecated)
    sourceUri: ImageUri | None = None
    privateImageId: str | None = None
    contentDescription: LocalizedString | None = None

    @model_validator(mode="after")
    def _exactly_one_image_source(self) -> "Image":
        """Google rejects an Image carrying both a URI and a private image id.

        Setting neither stays permitted: an empty Image is used as a
        placeholder in existing code, and every field here is optional.
        """
        if self.sourceUri is not None and self.privateImageId is not None:
            raise ValueError(
                "Image cannot have both sourceUri and privateImageId set. "
                "Use sourceUri for publicly reachable images and "
                "privateImageId for an uploaded private image."
            )
        return self
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/test_api_private_image.py -v -p no:cacheprovider --no-cov`
Expected: PASS — 9 passed.

- [ ] **Step 6: Run the full suite — the validator touches shared model code**

Run: `pytest tests -v -p no:cacheprovider --no-cov -m "not integration"`
Expected: PASS. If a test fails because fixture data sets both fields on an `Image`, that fixture is wrong — Google would reject it. Fix the fixture, not the validator.

- [ ] **Step 7: Commit**

```bash
git add src/edutap/wallet_google/models/datatypes/private_content.py src/edutap/wallet_google/models/datatypes/general.py tests/test_api_private_image.py
git commit -m "feat: add UploadPrivateImageResponse and Image source validator

Adds the response model for the private image upload and a validator on
Image rejecting sourceUri and privateImageId together, which Google
otherwise rejects only server side on object insert."
```

---

### Task 3: Internal preparation and validation helpers

**Files:**
- Create: `src/edutap/wallet_google/_private_content.py`
- Test: `tests/test_api_private_image.py`

**Interfaces:**
- Consumes: `client_pool.upload_url()` and `Settings` fields from Task 1; `UploadPrivateImageResponse` from Task 2; `ImageData` from `edutap.wallet_google.models.handlers`.
- Produces:
  - `normalize_image_input(data: bytes | ImageData, mime_type: str | None) -> tuple[bytes, str]`
  - `resolve_issuer_id(issuer_id: str | None) -> str`
  - `validate_private_image(data: bytes, mime_type: str) -> None`
  - `prepare_private_image_upload(data, mime_type, issuer_id) -> tuple[str, bytes, dict[str, str]]` returning `(url, payload, headers)`
  - `PRIVATE_IMAGE_HINT: str` — the message appended to 403/404 errors

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_api_private_image.py`:

```python
# --- input normalisation -------------------------------------------------


def test_normalize_bytes_with_mime_type():
    from edutap.wallet_google._private_content import normalize_image_input

    assert normalize_image_input(b"raw", "image/png") == (b"raw", "image/png")


def test_normalize_image_data_takes_mime_type_from_model():
    from edutap.wallet_google._private_content import normalize_image_input
    from edutap.wallet_google.models.handlers import ImageData

    image_data = ImageData(mimetype="image/jpeg", data=b"raw")

    assert normalize_image_input(image_data, None) == (b"raw", "image/jpeg")


def test_normalize_bytes_without_mime_type_raises():
    from edutap.wallet_google._private_content import normalize_image_input

    with pytest.raises(ValueError, match="mime_type is required"):
        normalize_image_input(b"raw", None)


def test_normalize_image_data_with_mime_type_raises():
    from edutap.wallet_google._private_content import normalize_image_input
    from edutap.wallet_google.models.handlers import ImageData

    image_data = ImageData(mimetype="image/jpeg", data=b"raw")

    with pytest.raises(ValueError, match="must not be given"):
        normalize_image_input(image_data, "image/png")


# --- issuer id -----------------------------------------------------------


def test_resolve_issuer_id_prefers_the_argument(mock_settings):
    from edutap.wallet_google._private_content import resolve_issuer_id

    mock_settings.issuer_id = "from-settings"

    assert resolve_issuer_id("explicit") == "explicit"


def test_resolve_issuer_id_falls_back_to_settings(mock_settings):
    from edutap.wallet_google._private_content import resolve_issuer_id

    mock_settings.issuer_id = "from-settings"

    assert resolve_issuer_id(None) == "from-settings"


def test_resolve_issuer_id_without_any_source_raises(mock_settings):
    from edutap.wallet_google._private_content import resolve_issuer_id

    mock_settings.issuer_id = ""

    with pytest.raises(ValueError, match="EDUTAP_WALLET_GOOGLE_ISSUER_ID"):
        resolve_issuer_id(None)


# --- guardrails ----------------------------------------------------------


def test_validate_private_image_accepts_allowed_type(mock_settings):
    from edutap.wallet_google._private_content import validate_private_image

    assert validate_private_image(b"raw", "image/png") is None


def test_validate_private_image_rejects_disallowed_type(mock_settings):
    from edutap.wallet_google._private_content import validate_private_image

    with pytest.raises(ValueError, match="image/tiff"):
        validate_private_image(b"raw", "image/tiff")


def test_validate_private_image_rejects_oversized_payload(mock_settings):
    from edutap.wallet_google._private_content import validate_private_image

    mock_settings.private_image_max_bytes = 4

    with pytest.raises(ValueError, match="exceeds"):
        validate_private_image(b"more than four bytes", "image/png")


def test_validate_private_image_size_check_disabled_by_zero(mock_settings):
    from edutap.wallet_google._private_content import validate_private_image

    mock_settings.private_image_max_bytes = 0

    assert validate_private_image(b"more than four bytes", "image/png") is None


# --- request preparation -------------------------------------------------


def test_prepare_private_image_upload(mock_settings):
    from edutap.wallet_google._private_content import prepare_private_image_upload

    url, payload, headers = prepare_private_image_upload(
        b"raw", "image/png", "3388000000012345"
    )

    assert url == (
        "https://walletobjects.googleapis.com/upload/walletobjects/v1"
        "/privateContent/3388000000012345/uploadPrivateImage"
    )
    assert payload == b"raw"
    assert headers == {"Content-Type": "image/png"}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_api_private_image.py -v -p no:cacheprovider --no-cov`
Expected: FAIL — `ModuleNotFoundError: No module named 'edutap.wallet_google._private_content'`.

- [ ] **Step 3: Create the module**

Create `src/edutap/wallet_google/_private_content.py`:

```python
"""Internal helpers for the Google Wallet privateContent endpoints.

This module is not public API. Use the functions in
:mod:`edutap.wallet_google.api` instead.

The `uploadPrivateImage` method is missing from the Google Wallet discovery
document and from every generated Google client library. It is documented only
through a code sample at
https://developers.google.com/wallet/generic/use-cases/secure-private-images
so the request is assembled by hand here.
"""

from .clientpool import client_pool
from .models.handlers import ImageData

import logging


logger = logging.getLogger(__name__)


PRIVATE_IMAGE_HINT = (
    "private images may need to be enabled for this issuer by Google support"
)


def normalize_image_input(
    data: bytes | ImageData,
    mime_type: str | None,
) -> tuple[bytes, str]:
    """Reduce the accepted input forms to raw bytes plus a mime type.

    :param data:        Raw image bytes, or an ImageData instance as returned
                        by an ImageProvider plugin.
    :param mime_type:   Mime type of the image. Required for bytes, and
                        forbidden for ImageData, which carries its own.
    :raises ValueError: When the combination of data and mime_type is invalid.
    :return:            Tuple of image bytes and mime type.
    """
    if isinstance(data, ImageData):
        if mime_type is not None:
            raise ValueError(
                "mime_type must not be given together with an ImageData "
                "instance, it already carries its mimetype"
            )
        return data.data, data.mimetype
    if mime_type is None:
        raise ValueError("mime_type is required when passing raw bytes")
    return data, mime_type


def resolve_issuer_id(issuer_id: str | None) -> str:
    """Determine the issuer id to use, falling back to the settings.

    :param issuer_id:   Explicitly given issuer id, or None.
    :raises ValueError: When neither an argument nor a setting is available.
    :return:            The issuer id to use.
    """
    resolved = issuer_id or client_pool.settings.issuer_id
    if not resolved:
        raise ValueError(
            "No issuer_id given and none configured. Pass issuer_id= or set "
            "EDUTAP_WALLET_GOOGLE_ISSUER_ID."
        )
    return resolved


def validate_private_image(data: bytes, mime_type: str) -> None:
    """Check the payload against the configured guardrails.

    Google documents no size or format limits for this endpoint, so both
    checks are configurable and deliberately generous. Failing here saves a
    request against the API rate limit and produces a readable message
    instead of an opaque server error.

    :param data:        Image bytes.
    :param mime_type:   Mime type of the image.
    :raises ValueError: When the mime type is not allowed or the payload is
                        larger than the configured maximum.
    """
    settings = client_pool.settings
    allowed = settings.private_image_allowed_mime_types
    if mime_type not in allowed:
        raise ValueError(
            f"Mime type {mime_type} is not allowed for private images. "
            f"Allowed: {', '.join(allowed)}. Override with "
            f"EDUTAP_WALLET_GOOGLE_PRIVATE_IMAGE_ALLOWED_MIME_TYPES."
        )
    max_bytes = settings.private_image_max_bytes
    if max_bytes and len(data) > max_bytes:
        raise ValueError(
            f"Image of {len(data)} bytes exceeds the configured maximum of "
            f"{max_bytes} bytes. Override with "
            f"EDUTAP_WALLET_GOOGLE_PRIVATE_IMAGE_MAX_BYTES, 0 disables the check."
        )
    return None


def prepare_private_image_upload(
    data: bytes | ImageData,
    mime_type: str | None,
    issuer_id: str | None,
) -> tuple[str, bytes, dict[str, str]]:
    """Normalise, validate and build everything the HTTP call needs.

    :param data:        Raw image bytes or an ImageData instance.
    :param mime_type:   Mime type, required for bytes.
    :param issuer_id:   Issuer id, or None to use the configured default.
    :raises ValueError: On any invalid input.
    :return:            Tuple of url, request body and request headers.
    """
    payload, resolved_mime_type = normalize_image_input(data, mime_type)
    validate_private_image(payload, resolved_mime_type)
    resolved_issuer_id = resolve_issuer_id(issuer_id)
    url = client_pool.upload_url(
        f"/privateContent/{resolved_issuer_id}/uploadPrivateImage"
    )
    headers = {"Content-Type": resolved_mime_type}
    logger.debug("Uploading %d bytes of %s to %s", len(payload), resolved_mime_type, url)
    return url, payload, headers
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_api_private_image.py -v -p no:cacheprovider --no-cov`
Expected: PASS — 21 passed.

- [ ] **Step 5: Commit**

```bash
git add src/edutap/wallet_google/_private_content.py tests/test_api_private_image.py
git commit -m "feat: add internal helpers for private image uploads

Normalises bytes or ImageData input, resolves the issuer id against the
settings, applies the configurable mime type and size guardrails, and
builds the upload request."
```

---

### Task 4: Error hint in `handle_response_errors`

**Files:**
- Modify: `src/edutap/wallet_google/utils.py:111-157`
- Test: `tests/test_api_private_image.py`

**Interfaces:**
- Consumes: `PRIVATE_IMAGE_HINT` from Task 3.
- Produces: `handle_response_errors(response, operation, name, resource_id="", allow_409=False, hint="")` — the `hint` is appended to the 403 access-denied and 404 messages.

Note: the existing `name` parameter is only used for message text, it is never looked up in the registry, so passing `"PrivateImage"` needs no other change. Only the hint is new.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_api_private_image.py`:

```python
# --- error hint ----------------------------------------------------------


def test_handle_response_errors_appends_hint_on_403():
    from edutap.wallet_google.exceptions import WalletException
    from edutap.wallet_google.utils import handle_response_errors

    import httpx

    response = httpx.Response(403, text="forbidden")

    with pytest.raises(WalletException, match="ask support"):
        handle_response_errors(
            response, "upload", "PrivateImage", hint="ask support"
        )


def test_handle_response_errors_appends_hint_on_404():
    from edutap.wallet_google.utils import handle_response_errors

    import httpx

    response = httpx.Response(404, text="not found")

    with pytest.raises(LookupError, match="ask support"):
        handle_response_errors(
            response, "upload", "PrivateImage", hint="ask support"
        )


def test_handle_response_errors_without_hint_is_unchanged():
    from edutap.wallet_google.utils import handle_response_errors

    import httpx

    response = httpx.Response(404, text="not found")

    with pytest.raises(LookupError) as excinfo:
        handle_response_errors(response, "read", "GenericObject")

    assert str(excinfo.value) == "GenericObject not found: not found"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_api_private_image.py -k handle_response -v -p no:cacheprovider --no-cov`
Expected: FAIL — `TypeError: handle_response_errors() got an unexpected keyword argument 'hint'`.

- [ ] **Step 3: Add the hint parameter**

In `src/edutap/wallet_google/utils.py`, change the signature and the two message sites:

```python
def handle_response_errors(
    response,
    operation: str,
    name: str,
    resource_id: str = "",
    allow_409: bool = False,
    hint: str = "",
) -> None:
    """Handle HTTP response errors and raise appropriate exceptions.

    :param response:     HTTP response object (from requests or httpx)
    :param operation:    Operation name for error messages (e.g., "create", "read")
    :param name:         Resource name for error messages
    :param resource_id:  Resource ID for error messages
    :param allow_409:    If True, don't raise exception on 409 (for create operations)
    :param hint:         Optional extra note appended to access denied and not
                         found messages, for endpoints whose failure mode is
                         hard to diagnose from the status code alone.
    :raises QuotaExceededException: When API quota exceeded
    :raises LookupError:            When resource not found (404)
    :raises ObjectAlreadyExistsException: When resource already exists (409)
    :raises WalletException:        For other errors
    """
    from .exceptions import ObjectAlreadyExistsException
    from .exceptions import QuotaExceededException
    from .exceptions import WalletException

    if response.status_code == 200:
        return

    hint_suffix = f" ({hint})" if hint else ""

    if response.status_code == 403:
        response_lower = response.text.lower()
        # Use word boundaries to avoid false positives like "accurate", "separate"
        if re.search(r"\b(quota|rate limit|rate-limit)\b", response_lower):
            raise QuotaExceededException(
                f"Quota exceeded while trying to {operation} {name} {resource_id}"
            )
        raise WalletException(
            f"Access denied while trying to {operation} {name} {resource_id}: "
            f"{response.text}{hint_suffix}"
        )

    elif response.status_code == 404:
        raise LookupError(f"{name} not found: {response.text}{hint_suffix}")

    elif response.status_code == 409:
        if allow_409:
            return
        raise ObjectAlreadyExistsException(
            f"{name} {resource_id} already exists\n{response.text}"
        )
    raise WalletException(f"Error: {response.status_code} - {response.text}")
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_api_private_image.py -v -p no:cacheprovider --no-cov`
Expected: PASS — 24 passed.

- [ ] **Step 5: Run the full suite — this function is used by every API call**

Run: `pytest tests -v -p no:cacheprovider --no-cov -m "not integration"`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/edutap/wallet_google/utils.py tests/test_api_private_image.py
git commit -m "feat: allow an explanatory hint on response error messages

Access denied and not found on the private image endpoint are plausible
outcomes of a missing feature enablement rather than of a wrong request.
The hint gives the caller somewhere to look."
```

---

### Task 5: Public upload functions, sync and async

**Files:**
- Modify: `src/edutap/wallet_google/api.py:68-81` (`__all__`), and append two functions to each of the "Synchronous API" and "Asynchronous API" sections
- Test: `tests/test_api_private_image.py`

**Interfaces:**
- Consumes: `prepare_private_image_upload()`, `PRIVATE_IMAGE_HINT` (Task 3); `handle_response_errors(..., hint=)` (Task 4); `UploadPrivateImageResponse` (Task 2).
- Produces:
  - `api.upload_private_image(data: bytes | ImageData, mime_type: str | None = None, *, issuer_id: str | None = None, credentials: dict | None = None) -> str`
  - `api.aupload_private_image(...)` — same signature, coroutine

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_api_private_image.py`. Add the imports at the top of the file first:

```python
import httpx
import respx
```

Then the tests:

```python
# --- upload, sync and async ----------------------------------------------


ISSUER_ID = "3388000000012345"


def _upload_url() -> str:
    return client_pool.upload_url(
        f"/privateContent/{ISSUER_ID}/uploadPrivateImage"
    )


@respx.mock
def test_upload_private_image_returns_id(mock_session, mock_settings):
    from edutap.wallet_google import api

    respx.post(_upload_url()).mock(
        return_value=httpx.Response(200, json={"privateImageId": "abc123"})
    )

    result = api.upload_private_image(b"raw", "image/png", issuer_id=ISSUER_ID)

    assert result == "abc123"


@respx.mock
def test_upload_private_image_sends_raw_body_and_content_type(
    mock_session, mock_settings
):
    from edutap.wallet_google import api

    respx.post(_upload_url()).mock(
        return_value=httpx.Response(200, json={"privateImageId": "abc123"})
    )

    api.upload_private_image(b"raw-bytes", "image/jpeg", issuer_id=ISSUER_ID)

    request = respx.calls.last.request
    assert request.content == b"raw-bytes"
    assert request.headers["Content-Type"] == "image/jpeg"


@respx.mock
def test_upload_private_image_accepts_image_data(mock_session, mock_settings):
    from edutap.wallet_google import api
    from edutap.wallet_google.models.handlers import ImageData

    respx.post(_upload_url()).mock(
        return_value=httpx.Response(200, json={"privateImageId": "abc123"})
    )

    result = api.upload_private_image(
        ImageData(mimetype="image/jpeg", data=b"raw"), issuer_id=ISSUER_ID
    )

    assert result == "abc123"
    assert respx.calls.last.request.headers["Content-Type"] == "image/jpeg"


@respx.mock
def test_upload_private_image_uses_settings_issuer_id(mock_session, mock_settings):
    from edutap.wallet_google import api

    mock_settings.issuer_id = ISSUER_ID
    respx.post(_upload_url()).mock(
        return_value=httpx.Response(200, json={"privateImageId": "abc123"})
    )

    assert api.upload_private_image(b"raw", "image/png") == "abc123"


@respx.mock
def test_upload_private_image_403_mentions_the_hint(mock_session, mock_settings):
    from edutap.wallet_google import api
    from edutap.wallet_google.exceptions import WalletException

    respx.post(_upload_url()).mock(
        return_value=httpx.Response(403, text="denied")
    )

    with pytest.raises(WalletException, match="Google support"):
        api.upload_private_image(b"raw", "image/png", issuer_id=ISSUER_ID)


@respx.mock
def test_upload_private_image_403_quota(mock_session, mock_settings):
    from edutap.wallet_google import api
    from edutap.wallet_google.exceptions import QuotaExceededException

    respx.post(_upload_url()).mock(
        return_value=httpx.Response(403, text="quota exceeded")
    )

    with pytest.raises(QuotaExceededException):
        api.upload_private_image(b"raw", "image/png", issuer_id=ISSUER_ID)


@respx.mock
def test_upload_private_image_404(mock_session, mock_settings):
    from edutap.wallet_google import api

    respx.post(_upload_url()).mock(return_value=httpx.Response(404, text="nope"))

    with pytest.raises(LookupError):
        api.upload_private_image(b"raw", "image/png", issuer_id=ISSUER_ID)


@respx.mock
def test_upload_private_image_500(mock_session, mock_settings):
    from edutap.wallet_google import api
    from edutap.wallet_google.exceptions import WalletException

    respx.post(_upload_url()).mock(return_value=httpx.Response(500, text="boom"))

    with pytest.raises(WalletException):
        api.upload_private_image(b"raw", "image/png", issuer_id=ISSUER_ID)


def test_upload_private_image_rejects_bytes_without_mime_type(mock_settings):
    from edutap.wallet_google import api

    with pytest.raises(ValueError, match="mime_type is required"):
        api.upload_private_image(b"raw", None, issuer_id=ISSUER_ID)


@pytest.mark.asyncio
@respx.mock
async def test_aupload_private_image_returns_id(mock_async_session, mock_settings):
    from edutap.wallet_google import api

    respx.post(_upload_url()).mock(
        return_value=httpx.Response(200, json={"privateImageId": "abc123"})
    )

    result = await api.aupload_private_image(
        b"raw", "image/png", issuer_id=ISSUER_ID
    )

    assert result == "abc123"


@pytest.mark.asyncio
@respx.mock
async def test_aupload_private_image_sends_raw_body(
    mock_async_session, mock_settings
):
    from edutap.wallet_google import api

    respx.post(_upload_url()).mock(
        return_value=httpx.Response(200, json={"privateImageId": "abc123"})
    )

    await api.aupload_private_image(b"raw-bytes", "image/jpeg", issuer_id=ISSUER_ID)

    request = respx.calls.last.request
    assert request.content == b"raw-bytes"
    assert request.headers["Content-Type"] == "image/jpeg"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_api_private_image.py -k upload_private_image -v -p no:cacheprovider --no-cov`
Expected: FAIL — `AttributeError: module 'edutap.wallet_google.api' has no attribute 'upload_private_image'`.

- [ ] **Step 3: Add the imports and exports to `api.py`**

Add to the import block, keeping the existing alphabetical grouping style:

```python
from ._private_content import prepare_private_image_upload
from ._private_content import PRIVATE_IMAGE_HINT
from .clientpool import client_pool
from .credentials import credentials_manager
from .models.bases import make_partial_model
from .models.bases import Model
from .models.datatypes.general import PaginatedResponse
from .models.datatypes.general import Pagination
from .models.datatypes.jwt import JWTClaims
from .models.datatypes.jwt import JWTPayload
from .models.datatypes.message import Message
from .models.datatypes.private_content import UploadPrivateImageResponse
from .models.handlers import ImageData
from .models.misc import AddMessageRequest
```

Extend `__all__`:

```python
__all__ = [
    "new",
    "save_link",
    "create",
    "read",
    "update",
    "message",
    "listing",
    "upload_private_image",
    "acreate",
    "aread",
    "aupdate",
    "amessage",
    "alisting",
    "aupload_private_image",
]
```

- [ ] **Step 4: Add the sync function**

Append to the end of the "Synchronous API" section of `api.py`, directly after `listing()`:

```python
def upload_private_image(
    data: bytes | ImageData,
    mime_type: str | None = None,
    *,
    issuer_id: str | None = None,
    credentials: dict | None = None,
) -> str:
    """Uploads a private image and returns its identifier.

    A private image is not served from a publicly reachable URL. The returned
    identifier belongs into `Image.privateImageId`, which may be used on pass
    **objects** only, inside `imageModulesData`, and only for a single object.

    The identifier is returned exactly once. Google offers no way to list or
    delete private images, so the caller must persist it together with the
    object it belongs to. See the documentation for the full lifecycle.

    see: https://developers.google.com/wallet/generic/use-cases/secure-private-images

    :param data:                    Raw image bytes, or an ImageData instance
                                    as returned by an ImageProvider plugin.
    :param mime_type:               Mime type of the image. Required when
                                    passing bytes, and forbidden when passing
                                    an ImageData instance.
    :param issuer_id:               Issuer id to upload for. Defaults to the
                                    configured EDUTAP_WALLET_GOOGLE_ISSUER_ID.
    :param credentials:             Optional session credentials as dict.
    :raises ValueError:             When the input, the mime type, the size or
                                    the issuer id is invalid.
    :raises QuotaExceededException: When the quota was exceeded.
    :raises LookupError:            When the endpoint answered 404.
    :raises WalletException:        When the response status code is not 200.
    :return:                        The privateImageId of the uploaded image.
    """
    url, payload, headers = prepare_private_image_upload(data, mime_type, issuer_id)

    client = client_pool.client(credentials=credentials)
    response = client.post(url=url, content=payload, headers=headers)

    handle_response_errors(
        response,
        "upload private image for",
        "PrivateImage",
        hint=PRIVATE_IMAGE_HINT,
    )
    return UploadPrivateImageResponse.model_validate_json(
        response.content
    ).privateImageId
```

Note `content=` rather than `data=`: the body is raw bytes, and httpx deprecates `data=` for that.

- [ ] **Step 5: Add the async function**

Append to the end of the "Asynchronous API" section, directly after `alisting()`:

```python
async def aupload_private_image(
    data: bytes | ImageData,
    mime_type: str | None = None,
    *,
    issuer_id: str | None = None,
    credentials: dict | None = None,
) -> str:
    """Uploads a private image asynchronously and returns its identifier.

    See `upload_private_image` for the full description, the constraints
    Google places on private images, and the obligation to persist the
    returned identifier.

    :param data:                    Raw image bytes, or an ImageData instance
                                    as returned by an ImageProvider plugin.
    :param mime_type:               Mime type of the image. Required when
                                    passing bytes, and forbidden when passing
                                    an ImageData instance.
    :param issuer_id:               Issuer id to upload for. Defaults to the
                                    configured EDUTAP_WALLET_GOOGLE_ISSUER_ID.
    :param credentials:             Optional session credentials as dict.
    :raises ValueError:             When the input, the mime type, the size or
                                    the issuer id is invalid.
    :raises QuotaExceededException: When the quota was exceeded.
    :raises LookupError:            When the endpoint answered 404.
    :raises WalletException:        When the response status code is not 200.
    :return:                        The privateImageId of the uploaded image.
    """
    url, payload, headers = prepare_private_image_upload(data, mime_type, issuer_id)

    client = client_pool.async_client(credentials=credentials)
    response = await client.post(url=url, content=payload, headers=headers)

    handle_response_errors(
        response,
        "upload private image for",
        "PrivateImage",
        hint=PRIVATE_IMAGE_HINT,
    )
    return UploadPrivateImageResponse.model_validate_json(
        response.content
    ).privateImageId
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `pytest tests/test_api_private_image.py -v -p no:cacheprovider --no-cov`
Expected: PASS — 35 passed.

If the 403 hint test fails on the match, check that `PRIVATE_IMAGE_HINT` contains the words "Google support".

- [ ] **Step 7: Commit**

```bash
git add src/edutap/wallet_google/api.py tests/test_api_private_image.py
git commit -m "feat: add upload_private_image and aupload_private_image

Uploads raw image bytes or an ImageData instance to the Google Wallet
privateContent endpoint and returns the privateImageId for use in
Image.privateImageId."
```

---

### Task 6: ImageProvider plugin bridge

**Files:**
- Modify: `src/edutap/wallet_google/_private_content.py` (add `image_data_by_id()`)
- Modify: `src/edutap/wallet_google/api.py` (two more functions, `__all__`)
- Test: `tests/test_api_private_image.py`

**Interfaces:**
- Consumes: `get_image_providers()` from `edutap.wallet_google.plugins`; `upload_private_image` / `aupload_private_image` from Task 5.
- Produces:
  - `_private_content.image_data_by_id(image_id: str) -> ImageData` (coroutine)
  - `api.upload_private_image_by_id(image_id: str, *, issuer_id: str | None = None, credentials: dict | None = None) -> str`
  - `api.aupload_private_image_by_id(...)` — same signature, coroutine

The registered test plugin `TestImageProvider` in `tests/data/test_wallet_google_plugins/plugins.py` answers `image_by_id("OK")` with `ImageData(mimetype="image/jpeg", data=b"mock-a-jepg")` and raises `LookupError` for `"ERROR"`. Use those ids.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_api_private_image.py`:

```python
# --- ImageProvider bridge ------------------------------------------------


@pytest.fixture
def single_image_provider():
    """Isolate these tests from the process-wide plugin registry.

    `plugins.add_plugin()` appends to a module-level list that nothing ever
    cleans up, so an earlier test file can leave a second ImageProvider
    registered and make these tests fail with "Multiple ImageProvider
    plugins registered". Clearing the runtime registry leaves exactly the one
    provider registered through entry points.
    """
    from edutap.wallet_google.plugins import _PLUGIN_REGISTRY

    saved = _PLUGIN_REGISTRY["ImageProvider"]
    _PLUGIN_REGISTRY["ImageProvider"] = []
    yield
    _PLUGIN_REGISTRY["ImageProvider"] = saved


@respx.mock
def test_upload_private_image_by_id(
    mock_session, mock_settings, single_image_provider
):
    from edutap.wallet_google import api

    respx.post(_upload_url()).mock(
        return_value=httpx.Response(200, json={"privateImageId": "abc123"})
    )

    result = api.upload_private_image_by_id("OK", issuer_id=ISSUER_ID)

    assert result == "abc123"
    request = respx.calls.last.request
    assert request.content == b"mock-a-jepg"
    assert request.headers["Content-Type"] == "image/jpeg"


@pytest.mark.asyncio
@respx.mock
async def test_aupload_private_image_by_id(
    mock_async_session, mock_settings, single_image_provider
):
    from edutap.wallet_google import api

    respx.post(_upload_url()).mock(
        return_value=httpx.Response(200, json={"privateImageId": "abc123"})
    )

    result = await api.aupload_private_image_by_id("OK", issuer_id=ISSUER_ID)

    assert result == "abc123"
    assert respx.calls.last.request.content == b"mock-a-jepg"


@pytest.mark.asyncio
async def test_aupload_private_image_by_id_propagates_lookup_error(
    mock_async_session, mock_settings, single_image_provider
):
    from edutap.wallet_google import api

    with pytest.raises(LookupError):
        await api.aupload_private_image_by_id("ERROR", issuer_id=ISSUER_ID)


@pytest.mark.asyncio
async def test_sync_by_id_inside_running_loop_raises(mock_settings):
    """The sync bridge cannot start a loop inside one, so it must say so.

    No provider fixture needed: the guard fires before any plugin lookup.
    """
    from edutap.wallet_google import api

    with pytest.raises(RuntimeError, match="aupload_private_image_by_id"):
        api.upload_private_image_by_id("OK", issuer_id=ISSUER_ID)


@pytest.mark.asyncio
async def test_image_data_by_id_rejects_multiple_providers(monkeypatch):
    from edutap.wallet_google import _private_content
    from edutap.wallet_google.models.handlers import ImageData

    class OtherProvider:
        async def image_by_id(self, image_id: str) -> ImageData:
            return ImageData(mimetype="image/png", data=b"other")

    monkeypatch.setattr(
        "edutap.wallet_google._private_content.get_image_providers",
        lambda: [OtherProvider(), OtherProvider()],
    )

    with pytest.raises(ValueError, match="Multiple"):
        await _private_content.image_data_by_id("OK")


@pytest.mark.asyncio
async def test_image_data_by_id_without_any_provider(monkeypatch):
    from edutap.wallet_google import _private_content

    monkeypatch.setattr(
        "edutap.wallet_google.plugins.entry_points",
        lambda *args, **kwargs: [],
    )

    with pytest.raises(NotImplementedError):
        await _private_content.image_data_by_id("OK")
```

Note on the last test: `get_image_providers()` discovers plugins through entry
points and raises `NotImplementedError` when it finds none, so the entry point
lookup is what has to be patched — patching `get_image_providers` itself would
test nothing.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_api_private_image.py -k by_id -v -p no:cacheprovider --no-cov`
Expected: FAIL — `AttributeError: module 'edutap.wallet_google.api' has no attribute 'upload_private_image_by_id'`.

- [ ] **Step 3: Add `image_data_by_id()` to `_private_content.py`**

Add the import at the top of `_private_content.py`:

```python
from .plugins import get_image_providers
```

Append the function:

```python
async def image_data_by_id(image_id: str) -> ImageData:
    """Fetch an image from the registered ImageProvider plugin.

    :param image_id:              Identifier the ImageProvider understands.
    :raises NotImplementedError:  When no ImageProvider plugin is registered.
    :raises ValueError:           When more than one ImageProvider is
                                  registered, since there is no way to decide
                                  which one to ask.
    :raises LookupError:          When the provider does not know the id.
    :return:                      The image data.
    """
    providers = get_image_providers()
    if len(providers) > 1:
        raise ValueError(
            "Multiple ImageProvider plugins registered, cannot decide which "
            "one to ask for the image."
        )
    return await providers[0].image_by_id(image_id)
```

- [ ] **Step 4: Add the two public functions to `api.py`**

Add the imports:

```python
from ._private_content import image_data_by_id
```

and

```python
import asyncio
```

next to the existing `import datetime` / `import json` block.

Extend `__all__` with `"upload_private_image_by_id"` after `"upload_private_image"` and `"aupload_private_image_by_id"` after `"aupload_private_image"`.

Append to the "Synchronous API" section, after `upload_private_image()`:

```python
def upload_private_image_by_id(
    image_id: str,
    *,
    issuer_id: str | None = None,
    credentials: dict | None = None,
) -> str:
    """Uploads an image fetched from the registered ImageProvider plugin.

    Convenience wrapper around `upload_private_image` for applications that
    already serve their images through an ImageProvider. The plugin protocol
    is asynchronous, so this function runs a short event loop internally and
    therefore cannot be called from within a running one — use
    `aupload_private_image_by_id` there.

    :param image_id:              Identifier the ImageProvider understands.
    :param issuer_id:             Issuer id to upload for. Defaults to the
                                  configured EDUTAP_WALLET_GOOGLE_ISSUER_ID.
    :param credentials:           Optional session credentials as dict.
    :raises RuntimeError:         When called from within a running event loop.
    :raises NotImplementedError:  When no ImageProvider plugin is registered.
    :raises ValueError:           When more than one ImageProvider is registered.
    :raises LookupError:          When the provider does not know the id.
    :return:                      The privateImageId of the uploaded image.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass
    else:
        raise RuntimeError(
            "upload_private_image_by_id() cannot run inside an active event "
            "loop. Use aupload_private_image_by_id() instead."
        )

    image_data = asyncio.run(image_data_by_id(image_id))
    return upload_private_image(
        image_data,
        issuer_id=issuer_id,
        credentials=credentials,
    )
```

Append to the "Asynchronous API" section, after `aupload_private_image()`:

```python
async def aupload_private_image_by_id(
    image_id: str,
    *,
    issuer_id: str | None = None,
    credentials: dict | None = None,
) -> str:
    """Uploads an image fetched from the registered ImageProvider plugin.

    Asynchronous variant of `upload_private_image_by_id`, and the one to use
    inside FastAPI handlers or any other running event loop.

    :param image_id:              Identifier the ImageProvider understands.
    :param issuer_id:             Issuer id to upload for. Defaults to the
                                  configured EDUTAP_WALLET_GOOGLE_ISSUER_ID.
    :param credentials:           Optional session credentials as dict.
    :raises NotImplementedError:  When no ImageProvider plugin is registered.
    :raises ValueError:           When more than one ImageProvider is registered.
    :raises LookupError:          When the provider does not know the id.
    :return:                      The privateImageId of the uploaded image.
    """
    image_data = await image_data_by_id(image_id)
    return await aupload_private_image(
        image_data,
        issuer_id=issuer_id,
        credentials=credentials,
    )
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/test_api_private_image.py -v -p no:cacheprovider --no-cov`
Expected: PASS — 41 passed.

- [ ] **Step 6: Run the full suite**

Run: `pytest tests -v -p no:cacheprovider --no-cov -m "not integration"`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/edutap/wallet_google/_private_content.py src/edutap/wallet_google/api.py tests/test_api_private_image.py
git commit -m "feat: add ImageProvider bridge for private image uploads

upload_private_image_by_id and aupload_private_image_by_id fetch the image
from the registered ImageProvider plugin. The synchronous variant refuses
to run inside an active event loop instead of deadlocking."
```

---

### Task 7: Wire the configured issuer id into listing

**Files:**
- Modify: `src/edutap/wallet_google/api.py:340-375` (`_prepare_listing`)
- Test: `tests/test_api_private_image.py`

The docstrings of `listing()` and `alisting()` already promise that `issuer_id` falls back to `EDUTAP_WALLET_GOOGLE_ISSUER_ID`, but `Settings` had no such field until Task 1, so the fallback never existed. Close the gap now that the field is there.

**Interfaces:**
- Consumes: `Settings.issuer_id` (Task 1), read directly via `client_pool.settings`. Deliberately **not** `resolve_issuer_id()` from Task 3 — that helper raises a message worded for the upload endpoint, and listing needs its own.
- Produces: no new names — `_prepare_listing` gains the fallback.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_api_private_image.py`:

```python
# --- issuer id fallback in listing ---------------------------------------


@respx.mock
def test_listing_classes_falls_back_to_configured_issuer_id(
    mock_session, mock_settings
):
    from edutap.wallet_google import api

    mock_settings.issuer_id = ISSUER_ID
    respx.get(client_pool.url("GenericClass")).mock(
        return_value=httpx.Response(200, json={"resources": [], "pagination": None})
    )

    list(api.listing("GenericClass"))

    assert respx.calls.last.request.url.params["issuerId"] == ISSUER_ID


def test_listing_classes_without_any_issuer_id_raises(mock_session, mock_settings):
    from edutap.wallet_google import api

    mock_settings.issuer_id = ""

    with pytest.raises(ValueError, match="issuer_id"):
        list(api.listing("GenericClass"))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_api_private_image.py -k listing -v -p no:cacheprovider --no-cov`
Expected: FAIL — the first test raises `ValueError: issuer_id must be given to list classes` because no fallback exists yet.

- [ ] **Step 3: Add the fallback**

In `src/edutap/wallet_google/api.py`, inside `_prepare_listing`, replace the class branch:

```python
    elif name.endswith("Class"):
        is_pageable = True
        if not issuer_id:
            issuer_id = client_pool.settings.issuer_id
        if not issuer_id:
            raise ValueError(
                "issuer_id must be given to list classes, either as an "
                "argument or via EDUTAP_WALLET_GOOGLE_ISSUER_ID"
            )
        params["issuerId"] = issuer_id
        resource_identifier = issuer_id
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_api_private_image.py -v -p no:cacheprovider --no-cov`
Expected: PASS — 43 passed.

- [ ] **Step 5: Run the full suite — listing is widely used**

Run: `pytest tests -v -p no:cacheprovider --no-cov -m "not integration"`
Expected: PASS. If an existing test asserted the old error message, update the assertion — the message deliberately changed to name the environment variable.

- [ ] **Step 6: Commit**

```bash
git add src/edutap/wallet_google/api.py tests/test_api_private_image.py
git commit -m "fix: honour the configured issuer id when listing classes

The docstrings of listing() and alisting() already documented a fallback to
EDUTAP_WALLET_GOOGLE_ISSUER_ID, but Settings had no such field, so the
fallback never existed. It does now."
```

---

### Task 8: Lint, format and type check

**Files:** all of the above.

- [ ] **Step 1: Format**

Run: `uvx ruff format src tests`
Expected: files reformatted or "N files left unchanged".

- [ ] **Step 2: Lint**

Run: `uvx ruff check src tests --fix`
Expected: "All checks passed!"

The repository uses Plone-style isort rules: one import per line, `from x import y` sorted before plain `import x`. If ruff reorders your imports, keep its result.

- [ ] **Step 3: Type check**

Run: `uvx ty check`
Expected: no new errors compared to `main`. `bytes | ImageData` narrowing via `isinstance` should be understood; if `ty` complains about `data.data` on the union, the `isinstance` branch in `normalize_image_input` needs to return early, which it already does.

- [ ] **Step 4: Run everything once more**

Run: `pytest tests -v -p no:cacheprovider -m "not integration"`
Expected: PASS, coverage report printed.

- [ ] **Step 5: Commit any formatting changes**

```bash
git add -A src tests
git commit -m "style: apply ruff formatting"
```

Skip this commit if nothing changed.

---

### Task 9: Gated integration test

**Files:**
- Create: `tests/integration/test_private_image.py`
- Create: `tests/data/private_image_test.png` (a small real PNG)

**Interfaces:**
- Consumes: the full public API from Tasks 5 and 6.
- Produces: nothing other tasks depend on.

This test answers three questions the documentation leaves open, listed in the spec: whether the issuer needs enabling, whether one object may carry more than one private image, and whether a private image renders faithfully enough for a QR code to remain scannable. The third is manual.

It is double-gated: `@pytest.mark.integration` plus an environment variable, because every run leaves permanently undeletable images and objects at Google.

- [ ] **Step 1: Create the test image**

```bash
python3 -c "
import base64, pathlib
# 1x1 red PNG
png = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
)
pathlib.Path('tests/data/private_image_test.png').write_bytes(png)
print(len(png), 'bytes written')
"
```

Expected: `70 bytes written`

- [ ] **Step 2: Write the integration test**

Create `tests/integration/test_private_image.py`:

```python
"""Integration tests for private image uploads.

These run against the real Google Wallet API and are double-gated:

* `@pytest.mark.integration` plus `--run-integration`
* `EDUTAP_WALLET_GOOGLE_TEST_PRIVATE_IMAGES=1`

The second gate exists because private images may need to be enabled for the
issuer by Google support, and because neither uploaded images nor created
objects can be deleted — every run leaves permanent artefacts behind.

Open questions these tests are meant to answer, see
superpowers/specs/2026-07-20-private-image-upload-design.md:

1. Does a non-enabled issuer get a 403, a 404, or something else?
2. May one object carry more than one private image?
3. Does a private image render faithfully enough for a QR code to stay
   machine-readable? Manual, see `test_two_private_images_on_one_object`.
"""

from edutap.wallet_google import api
from edutap.wallet_google.settings import Settings
from pathlib import Path

import os
import pytest


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("EDUTAP_WALLET_GOOGLE_TEST_PRIVATE_IMAGES") != "1",
        reason=(
            "Private image tests leave undeletable artefacts at Google. "
            "Set EDUTAP_WALLET_GOOGLE_TEST_PRIVATE_IMAGES=1 to run them."
        ),
    ),
]

TEST_IMAGE = Path(__file__).parent.parent / "data" / "private_image_test.png"


@pytest.fixture
def issuer_id() -> str:
    settings = Settings()
    resolved = settings.issuer_id or settings.test_issuer_id
    if not resolved:
        pytest.skip(
            "Set EDUTAP_WALLET_GOOGLE_ISSUER_ID or "
            "EDUTAP_WALLET_GOOGLE_TEST_ISSUER_ID to run this test."
        )
    return resolved


def test_upload_returns_a_private_image_id(issuer_id):
    """Question 1: does the upload work for this issuer at all?

    If this fails with 403 or 404, record the exact status code and body in
    the spec — that answers whether the feature needs enabling.
    """
    private_image_id = api.upload_private_image(
        TEST_IMAGE.read_bytes(),
        "image/png",
        issuer_id=issuer_id,
    )

    assert private_image_id
    assert isinstance(private_image_id, str)


def test_two_private_images_on_one_object(issuer_id, integration_test_id):
    """Question 2: may a single object reference two private images?

    The European Student Card needs exactly this: a portrait and a QR code.
    If Google rejects the second reference, the ESC use case does not work
    and the spec must be corrected.

    Question 3 is manual: render the created object on a device and confirm
    that a real scanner still reads a QR code uploaded this way. Replace the
    test PNG with an actual QR code to do so.
    """
    photo_id = api.upload_private_image(
        TEST_IMAGE.read_bytes(), "image/png", issuer_id=issuer_id
    )
    qr_id = api.upload_private_image(
        TEST_IMAGE.read_bytes(), "image/png", issuer_id=issuer_id
    )

    assert photo_id != qr_id, "each upload must yield a fresh id"

    class_id = f"{issuer_id}.private-image-{integration_test_id}"
    api.create(api.new("GenericClass", {"id": class_id}))

    generic_object = api.new(
        "GenericObject",
        {
            "id": f"{class_id}.object",
            "classId": class_id,
            "state": "ACTIVE",
            "imageModulesData": [
                {"id": "photo", "mainImage": {"privateImageId": photo_id}},
                {"id": "qr_code", "mainImage": {"privateImageId": qr_id}},
            ],
        },
    )

    created = api.create(generic_object)

    assert len(created.imageModulesData) == 2


def test_a_private_image_cannot_be_reused(issuer_id, integration_test_id):
    """Google documents that one image serves exactly one object.

    Confirms the documented error rather than trusting the documentation.
    """
    from edutap.wallet_google.exceptions import WalletException

    private_image_id = api.upload_private_image(
        TEST_IMAGE.read_bytes(), "image/png", issuer_id=issuer_id
    )

    class_id = f"{issuer_id}.private-image-reuse-{integration_test_id}"
    api.create(api.new("GenericClass", {"id": class_id}))

    for suffix in ("first", "second"):
        generic_object = api.new(
            "GenericObject",
            {
                "id": f"{class_id}.{suffix}",
                "classId": class_id,
                "state": "ACTIVE",
                "imageModulesData": [
                    {"id": "photo", "mainImage": {"privateImageId": private_image_id}},
                ],
            },
        )
        if suffix == "first":
            api.create(generic_object)
            continue
        with pytest.raises(WalletException, match="already used"):
            api.create(generic_object)
```

- [ ] **Step 3: Verify the tests are skipped by default**

Run: `pytest tests/integration/test_private_image.py -v -p no:cacheprovider --no-cov --run-integration`
Expected: 3 skipped, with the reason mentioning `EDUTAP_WALLET_GOOGLE_TEST_PRIVATE_IMAGES`.

- [ ] **Step 4: Verify they are also skipped without `--run-integration`**

Run: `pytest tests/integration/test_private_image.py -v -p no:cacheprovider --no-cov`
Expected: deselected or skipped — `pytest-explicit` excludes the `integration` marker by default.

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_private_image.py tests/data/private_image_test.png
git commit -m "test: add gated integration tests for private image uploads

Double-gated behind the integration marker and
EDUTAP_WALLET_GOOGLE_TEST_PRIVATE_IMAGES, since neither uploaded images nor
created objects can be deleted. Answers whether the feature needs enabling
for the issuer and whether one object may carry two private images."
```

- [ ] **Step 6: Record the findings**

If you can run these against a real issuer, write the results into
`superpowers/specs/2026-07-20-private-image-upload-design.md`, replacing
the "unverified" markers in *Endpoint contract* and in *Open questions this
example raises*. If you cannot, leave them and say so in the handover.

---

### Task 10: Documentation

**Files:**
- Modify: `docs/tutorials.md`, `docs/reference.md`, `docs/explanation.md`, `README.md`

Read the *Documentation* and *Worked example* sections of the spec first — they contain the full prose, the comparison table and the ESC example. This task transfers that material into the docs, it does not invent new content.

- [ ] **Step 1: Add the how-to to `docs/tutorials.md`**

Match the surrounding heading level and MyST style. Two sections:

1. *Upload a private image* — upload, place the id in `imageModulesData`, create the object. Use the ESC example from the spec's *Before and after* subsection verbatim.
2. *Show a private image on the front of the card* — the `classTemplateInfo.cardTemplateOverride` snippet from the spec's `docs/tutorials.md` subsection verbatim. Explain that `imageModulesData` otherwise renders in the details view only, and that the module ids in the object must match the `fieldPath` entries in the class template.

- [ ] **Step 2: Add the API reference to `docs/reference.md`**

Document, matching the existing entries' style:

- `upload_private_image(data, mime_type=None, *, issuer_id=None, credentials=None) -> str`
- `aupload_private_image(...)`
- `upload_private_image_by_id(image_id, *, issuer_id=None, credentials=None) -> str`
- `aupload_private_image_by_id(...)`
- the four new settings with their defaults
- the `Image` validator
- the table of server-side error messages from the spec's *Server-side error messages* section, each with its remedy — in particular that `already used with object` requires a re-upload, not a retry

- [ ] **Step 3: Add the explanation to `docs/explanation.md`**

Two sections, both taken from the spec's `docs/explanation.md` subsection:

1. *Private image or ImageProvider?* — including the comparison table verbatim.
2. *Lifecycle and the obligation to persist the id* — the three properties (returned once, no delete, one object per image), the three consequences for the caller, and the example SQL table. State plainly that the library stores nothing and that this is an application decision.

- [ ] **Step 4: Add the paragraph to `README.md`**

Three or four sentences near the existing feature list: private images exist, they may need enabling by Google support, and the caller must persist the returned id because it can be neither listed nor deleted. Link to the explanation page.

- [ ] **Step 5: Check the docs build**

Run: `uvx tox -e docs` if that environment exists, otherwise check `tox.ini` for the documentation environment name and use it. If the project has no docs build environment, verify the MyST syntax by eye against neighbouring sections and move on.
Expected: build succeeds without new warnings.

- [ ] **Step 6: Spell check**

Run: `uvx codespell --skip "tests/data/*.json"`
Expected: no findings.

- [ ] **Step 7: Commit**

```bash
git add docs README.md
git commit -m "docs: document private image uploads

Adds the how-to including the cardTemplateOverride needed to place the
image on the front of the card, the API and settings reference with the
server-side error messages, and an explanation covering the choice between
a private image and an ImageProvider plus the obligation to persist the
returned id."
```

---

### Task 11: Final verification

- [ ] **Step 1: Full test suite with coverage**

Run: `pytest tests -v -m "not integration"`
Expected: PASS. Note the coverage of `_private_content.py` — it should be at or near 100%, since every branch has a test.

- [ ] **Step 2: All pre-commit hooks**

Run: `uvx pre-commit run --all-files`
Expected: all hooks pass. `check-manifest` may complain about `tests/data/private_image_test.png`; if so, add it to `MANIFEST.in` following the existing pattern for test data and re-run.

- [ ] **Step 3: Tox matrix**

Run: `uvx tox`
Expected: PASS on every configured Python version.

- [ ] **Step 4: Review the diff against the spec**

Run: `git diff main --stat`

Check each spec section has a corresponding change. Report to the user:
- files changed
- tests run and their result
- which of the three integration-test questions remain unanswered
- any spec statement still marked unverified

- [ ] **Step 5: Commit any fixes**

Only if steps 1 to 4 required changes.

Do **not** push. The user pushes.
