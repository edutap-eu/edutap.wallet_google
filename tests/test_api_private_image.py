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
