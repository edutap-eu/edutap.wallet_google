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

Before running these, note:

a. Expect the first test to fail, and treat that as the answer. The
   discovery document's description of `Image.privateImageId` ends with
   "Please contact support to use private images." — stronger evidence than
   this file's cautious "possibly gated" framing. A rejection on the very
   first upload is the likely outcome and a finding to record, not a bug to
   chase.
b. Every run of `test_two_private_images_on_one_object` costs two permanent
   artefacts: it uploads both images *before* attempting the create, so if
   Google rejects the second reference, two undeletable images are already
   orphaned — and re-running to confirm that costs two more.
c. A fully green run does NOT answer question 3. `tests/data/private_image_test.png`
   is a 70-byte placeholder. The docstrings below tell the runner to
   substitute a real QR code, but nothing fails, warns or skips if they
   don't, so all three tests can pass while question 3 remains exactly as
   open as before. If a QR code does not survive Google's re-encoding, the
   student ID card use case is dead regardless of how questions 1 and 2
   resolve.
"""

from edutap.wallet_google import api
from edutap.wallet_google.models.passes import GenericObject
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

    This test verifies that both private image IDs are actually attached to
    the returned object. If the assertion fails:

    - If returned_ids contains only one ID: Google rejected the second private
      image and the ESC use case does not work as designed. Record this in
      superpowers/specs/2026-07-20-private-image-upload-design.md.
    - If returned_ids is empty or contains None values: Google does not echo
      privateImageId back in the create response. The check must be redone by
      calling api.read("GenericObject", object_id) on the created object.
    - Either outcome is a real finding to be recorded, not a test to loosen.
    - If a read or create fails with a Pydantic `ValidationError` naming
      "Image cannot have both sourceUri and privateImageId set": Google
      echoed both fields back on a response, the library's validator rejects
      it, and the object has become unreadable through this library. That is
      a finding to record, not a test to loosen either.

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

    # api.create() is annotated to return the Model base class, so narrow it
    # before reaching for pass-specific fields.
    assert isinstance(created, GenericObject)

    returned_ids = {
        module.mainImage.privateImageId
        for module in created.imageModulesData or []
        if module.mainImage is not None
    }
    assert returned_ids == {photo_id, qr_id}


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
