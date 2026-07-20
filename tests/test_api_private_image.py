"""Tests for the private image upload API."""

from edutap.wallet_google.clientpool import client_pool

import httpx
import pytest
import respx


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


# --- error hint ----------------------------------------------------------


def test_handle_response_errors_appends_hint_on_403():
    from edutap.wallet_google.exceptions import WalletException
    from edutap.wallet_google.utils import handle_response_errors

    import httpx

    response = httpx.Response(403, text="forbidden")

    with pytest.raises(WalletException, match="ask support"):
        handle_response_errors(response, "upload", "PrivateImage", hint="ask support")


def test_handle_response_errors_appends_hint_on_404():
    from edutap.wallet_google.utils import handle_response_errors

    import httpx

    response = httpx.Response(404, text="not found")

    with pytest.raises(LookupError, match="ask support"):
        handle_response_errors(response, "upload", "PrivateImage", hint="ask support")


def test_handle_response_errors_without_hint_is_unchanged():
    from edutap.wallet_google.utils import handle_response_errors

    import httpx

    response = httpx.Response(404, text="not found")

    with pytest.raises(LookupError) as excinfo:
        handle_response_errors(response, "read", "GenericObject")

    assert str(excinfo.value) == "GenericObject not found: not found"


# --- upload, sync and async ----------------------------------------------


ISSUER_ID = "3388000000012345"


def _upload_url() -> str:
    return client_pool.upload_url(f"/privateContent/{ISSUER_ID}/uploadPrivateImage")


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

    respx.post(_upload_url()).mock(return_value=httpx.Response(403, text="denied"))

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

    result = await api.aupload_private_image(b"raw", "image/png", issuer_id=ISSUER_ID)

    assert result == "abc123"


@pytest.mark.asyncio
@respx.mock
async def test_aupload_private_image_sends_raw_body(mock_async_session, mock_settings):
    from edutap.wallet_google import api

    respx.post(_upload_url()).mock(
        return_value=httpx.Response(200, json={"privateImageId": "abc123"})
    )

    await api.aupload_private_image(b"raw-bytes", "image/jpeg", issuer_id=ISSUER_ID)

    request = respx.calls.last.request
    assert request.content == b"raw-bytes"
    assert request.headers["Content-Type"] == "image/jpeg"


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
def test_upload_private_image_by_id(mock_session, mock_settings, single_image_provider):
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
