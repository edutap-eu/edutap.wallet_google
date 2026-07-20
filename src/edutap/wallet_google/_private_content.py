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
from .plugins import get_image_providers

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
    logger.debug(
        "Uploading %d bytes of %s to %s", len(payload), resolved_mime_type, url
    )
    return url, payload, headers


def log_raw_upload_response(response) -> None:
    """Log the raw body of a private image upload response before parsing it.

    Every other response in this library passes through
    `utils.parse_response_json`, which logs the raw body at `logger.debug`
    right before validating it. `upload_private_image` and
    `aupload_private_image` parse `UploadPrivateImageResponse` directly
    instead, since that response model needs none of the partial-model
    handling `parse_response_json` provides, so without this call their raw
    body would never be logged at all.

    That matters more here than anywhere else in the library: uploading a
    private image is the one operation that cannot be undone or retried for
    free. Google offers no way to list or delete a private image, so if
    `Model`'s `extra="forbid"` rejects an otherwise-200 body (an added
    field, an empty body, a proxy's HTML interstitial) and the id is lost,
    that image is orphaned at Google permanently, with no other way to
    recover the id. `logger.debug` is easy to leave disabled in a
    production deployment, so this logs at `logger.warning` instead, on the
    principle that a slightly noisier log beats an unrecoverable, silently
    lost id.

    :param response: HTTP response object (from httpx), already checked by
                     `handle_response_errors`.
    """
    logger.warning(f"RAW-Response (private image upload): {response.content!r}")


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
