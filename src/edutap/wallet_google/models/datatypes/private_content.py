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
