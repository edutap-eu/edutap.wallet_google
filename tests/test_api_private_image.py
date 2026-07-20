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
