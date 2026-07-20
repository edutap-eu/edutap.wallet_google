# Reference

## API Functions

All API functions are in the `api` module, which provides both synchronous and asynchronous operations:

```python
from edutap.wallet_google import api

# Synchronous usage
result = api.create(my_pass)

# Asynchronous usage
result = await api.acreate(my_pass)
```

**Naming Convention:**
- **Sync functions**: `create()`, `read()`, `update()`, `message()`, `listing()`
- **Async functions**: `acreate()`, `aread()`, `aupdate()`, `amessage()`, `alisting()`
- **Shared functions**: `new()` and `save_link()` work for both sync and async

To tell the API functions what kind of item to deal with, the first parameter is the registered name of the model (except for `save_link`).
Models can be the different top-level wallet-classes or -objects, but also issuers, permissions and such (see section models below).

### API Module

The `api` module provides all CRUD operations in both sync and async variants.
All functions use persistent, pooled HTTP clients managed by the `ClientPoolManager` for optimal connection reuse.

```{eval-rst}
.. currentmodule:: edutap.wallet_google.api


.. autosummary::
   :toctree: _autosummary

   new
   save_link
   create
   read
   update
   message
   listing
   upload_private_image
   upload_private_image_by_id
   acreate
   aread
   aupdate
   amessage
   alisting
   aupload_private_image
   aupload_private_image_by_id
```

**Usage Notes:**
- Sync functions use regular function calls: `result = api.create(data)`
- Async functions use `async`/`await`: `result = await api.acreate(data)`
- `new()` is synchronous for both - it just creates model instances
- `save_link()` is synchronous for both - it uses synchronous JWT signing and should not be awaited

### Private image upload

Four functions upload image bytes to Google and return an opaque
`privateImageId`, for use in `Image.privateImageId` on pass **objects**
(never on classes). The upload is one-way: Google offers no endpoint to list
or delete a private image afterwards, so the caller is solely responsible
for persisting the returned id. See
[Private image or ImageProvider?](explanation.md) and
[Lifecycle and the obligation to persist the id](explanation.md) in the
Explanations section before using this in an application.

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

All four return the bare `privateImageId` string — exactly the value that
belongs into `Image.privateImageId`.

`upload_private_image()` / `aupload_private_image()` accept `data` in two
forms:

- `bytes` — `mime_type` is then required; passing `None` raises `ValueError`.
- `ImageData` (`edutap.wallet_google.models.handlers.ImageData`, the type
  returned by an `ImageProvider` plugin's `image_by_id()`) — `mime_type` must
  be `None`, otherwise `ValueError`. The mime type is taken from
  `ImageData.mimetype`.

Paths and file-like objects are deliberately not accepted; callers read the
bytes themselves.

`upload_private_image_by_id()` / `aupload_private_image_by_id()` fetch the
image from the single registered `ImageProvider` plugin by `image_id`, then
upload it — more than one registered provider, or none, is an error. The
synchronous `upload_private_image_by_id()` bridges to the provider's async
`image_by_id()` by running a fresh event loop per call; called from within an
already running event loop it raises `RuntimeError` pointing at
`aupload_private_image_by_id()` instead of deadlocking. See
[Private image or ImageProvider?](explanation.md) for what this means for an
`ImageProvider` implementation that caches async resources.

`issuer_id` falls back to `Settings.issuer_id`
(`EDUTAP_WALLET_GOOGLE_ISSUER_ID`); when neither is given, a `ValueError` is
raised. `credentials` is passed to the client pool exactly like in every
other API function.

**Configuration:**

Private image upload settings are configured via environment variables — see
the configuration options section of the [installation guide](installation.md)
for `EDUTAP_WALLET_GOOGLE_UPLOAD_API_URL`, `EDUTAP_WALLET_GOOGLE_ISSUER_ID`,
`EDUTAP_WALLET_GOOGLE_PRIVATE_IMAGE_MAX_BYTES`, and `EDUTAP_WALLET_GOOGLE_PRIVATE_IMAGE_ALLOWED_MIME_TYPES`.
Violations raise `ValueError` before any HTTP request is made.

**Model validation:** `Image` accepts `sourceUri` or `privateImageId`, never
both — Google rejects an `Image` that sets both fields with a server-side
error. A Pydantic model validator on `Image` now catches that case
client-side and raises `ValueError` before any request is made. Leaving both
fields unset stays permitted: `Image()` is used as an empty placeholder in
existing code, and every field on `Image` is optional.

**Server-side error messages:** the following three messages are documented
by Google for this feature. Only the first can occur during the upload
itself; the other two are raised when the id is used on an object, that is
during `create()` or `update()`, and surface as `WalletException`.

| Message | Raised when | Remedy |
| --- | --- | --- |
| `Image cannot have both source_uri and private_image_id` | An `Image` sets both fields, on object insert/patch. | Prevented client-side by the `Image` validator above; if it is seen anyway, remove one of the two fields. |
| `Couldn't find private image with id %s for issuer %s` | A non-existent id is set on an object. | Re-upload the image and use the fresh id. |
| `Couldn't add private image with id %s for issuer %s to object %s because it is already used with object %s. A private image can only be used with one object.` | The same id is used on a second object — Google enforces one image per object. | Re-upload the image to obtain a fresh id for the new object. This is a re-upload, not a retry: retrying with the same id fails again. |

## Models

### Base Models

```{eval-rst}

.. rubric:: General Base Models

`edutap.wallet_google.models.bases`

.. currentmodule:: edutap.wallet_google.models.bases

.. autosummary::
   :toctree: _autosummary

   Model
   WithIdModel
   CamelCaseAliasEnum
```

### Pass Models


```{eval-rst}

.. rubric:: Pass Base Models and Helpers

`edutap.wallet_google.models.passes.bases`

.. currentmodule:: edutap.wallet_google.models.passes.bases

.. autosummary::
   :toctree: _autosummary

   Reference
   ClassModel
   ObjectModel
   StyleableMixin
   CommonLogosMixin


.. rubric:: Generic

`edutap.wallet_google.models.passes.generic`

.. currentmodule:: edutap.wallet_google.models.passes.generic

.. autosummary::
   :toctree: _autosummary

   GenericClass
   GenericObject

.. rubric:: Retail

`edutap.wallet_google.models.passes.retail`

.. currentmodule:: edutap.wallet_google.models.passes.retail

.. autosummary::
   :toctree: _autosummary

   GiftCardClass
   GiftCardObject
   LoyaltyClass
   LoyaltyObject
   OfferClass
   OfferObject

.. rubric:: Ticket and Transit

`edutap.wallet_google.models.passes.tickets_and_transit`

.. currentmodule:: edutap.wallet_google.models.passes.tickets_and_transit

.. autosummary::
   :toctree: _autosummary

   EventTicketClass
   EventTicketObject
   TransitClass
   TransitObject
   FlightClass
   FlightObject

```

### Miscellaneous Models

```{eval-rst}

`edutap.wallet_google.models.misc`

.. currentmodule:: edutap.wallet_google.models.misc

.. rubric:: AddMessageRequest

.. autosummary::
   :toctree: _autosummary

   AddMessageRequest

.. rubric:: Issuer

.. autosummary::
   :toctree: _autosummary

   Issuer
   Permissions
   SmartTap

.. rubric:: JWT

.. autosummary::
   :toctree: _autosummary

   JwtResource
   JwtResponse
   Resources

```

### Handler Models

```{eval-rst}

`edutap.wallet_google.models.handlers`

.. currentmodule:: edutap.wallet_google.models.handlers

.. rubric:: Callback Models

.. autosummary::
   :toctree: _autosummary

   CallbackData
   SignedMessage
   IntermediateSigningKey
   SignedKey
   RootSigningPublicKey
   RootSigningPublicKeys

.. rubric:: Image Models

.. autosummary::
   :toctree: _autosummary

   ImageData

```

### Data Type Models

This are models for "Data Types" as Google names them, the sub schemas for nested objects.

```{eval-rst}


.. rubric:: data-types: Barcode

`edutap.wallet_google.models.datatypes.barcode`

.. currentmodule:: edutap.wallet_google.models.datatypes.barcode

.. autosummary::
   :toctree: _autosummary

   Barcode
   TotpParameters
   TotpDetails
   RotatingBarcode

.. rubric:: data-types: Class Template Info

`edutap.wallet_google.models.datatypes.class_template_info`

.. currentmodule:: edutap.wallet_google.models.datatypes.class_template_info

.. autosummary::
   :toctree: _autosummary

   FieldReference
   FieldSelector
   TemplateItem
   BarcodeSectionDetail
   CardBarcodeSectionDetails
   CardRowOneItem
   CardRowTwoItems
   CardRowThreeItems
   CardRowTemplateInfo
   CardTemplateOverride
   DetailsItemInfo
   DetailsTemplateOverride
   FirstRowOption
   ListTemplateOverride
   ClassTemplateInfo


.. rubric:: data-types: Data

`edutap.wallet_google.models.datatypes.data`

.. currentmodule:: edutap.wallet_google.models.datatypes.data

.. autosummary::
   :toctree: _autosummary

   TextModuleData
   LabelValue
   LabelValueRow
   LinksModuleData
   ImageModuleData
   InfoModuleData
   AppTarget
   AppLinkInfo
   AppLinkData

.. rubric:: data-types: Datetime

`edutap.wallet_google.models.datatypes.datetime`

.. currentmodule:: edutap.wallet_google.models.datatypes.datetime

.. autosummary::
   :toctree: _autosummary

   DateTime
   TimeInterval

.. rubric:: data-types: Enumerations

`edutap.wallet_google.models.datatypes.enums`

.. currentmodule:: edutap.wallet_google.models.datatypes.enums

.. autosummary::
   :toctree: _autosummary

   Action
   AnimationType
   BarcodeRenderEncoding
   BarcodeType
   ConfirmationCodeLabel
   DateFormat
   DoorsOpenLabel
   GateLabel
   GenericType
   MessageType
   MultipleDevicesAndHoldersAllowedStatus
   NfcConstraint
   PredefinedItem
   RedemptionChannel
   ReviewStatus
   Role
   RowLabel
   ScreenshotEligibility
   SeatLabel
   SectionLabel
   SharedDataType
   State
   RetailState
   TotpAlgorithm
   TransitOption
   ViewUnlockRequirement

.. rubric::  data-types: Event

`edutap.wallet_google.models.datatypes.event`

.. currentmodule:: edutap.wallet_google.models.datatypes.event

.. autosummary::
   :toctree: _autosummary

   EventSeat
   EventReservationInfo

.. rubric::  data-types: General

`edutap.wallet_google.models.datatypes.general`

.. currentmodule:: edutap.wallet_google.models.datatypes.general

.. autosummary::
   :toctree: _autosummary

   Uri
   ImageUri
   Image
   PassConstraints
   SecurityAnimation
   GroupingInfo
   Pagination
   PaginatedResponse
   CallbackOptions
   SaveRestrictions

.. rubric:: data-types: JWT

`edutap.wallet_google.models.datatypes.jwt`

.. currentmodule:: edutap.wallet_google.models.datatypes.jwt

.. autosummary::
   :toctree: _autosummary

   JWTPayload
   JWTClaims

.. rubric:: data-types: Localized String

`edutap.wallet_google.models.datatypes.localized_string`

.. currentmodule:: edutap.wallet_google.models.datatypes.localized_string

.. autosummary::
   :toctree: _autosummary

   TranslatedString
   LocalizedString

.. rubric:: data-types: Location

`edutap.wallet_google.models.datatypes.location`

.. currentmodule:: edutap.wallet_google.models.datatypes.location

.. autosummary::
   :toctree: _autosummary

   LatLongPoint

.. rubric::  data-types: Loyalty

.. currentmodule:: edutap.wallet_google.models.datatypes.loyalty

`edutap.wallet_google.models.datatypes.loyalty`

.. autosummary::
   :toctree: _autosummary

   LoyaltyPointsBalance
   LoyaltyPoints

.. rubric:: data-types: Message

`edutap.wallet_google.models.datatypes.message`

.. currentmodule:: edutap.wallet_google.models.datatypes.message

.. autosummary::
   :toctree: _autosummary

   Message

.. rubric:: data-types: Module Data

`edutap.wallet_google.models.datatypes.moduledata`

.. currentmodule:: edutap.wallet_google.models.datatypes.moduledata

.. autosummary::
   :toctree: _autosummary

   ModuleViewConstraints
   ValueAddedModuleData

.. rubric:: data-types: Money

`edutap.wallet_google.models.datatypes.money`

.. currentmodule:: edutap.wallet_google.models.datatypes.money

.. autosummary::
   :toctree: _autosummary

   Money

.. currentmodule:: edutap.wallet_google.models.datatypes.notification

.. rubric::  data-types: Notification

`edutap.wallet_google.models.datatypes.notification`

.. autosummary::
   :toctree: _autosummary

   Notifications
   ExpiryNotification
   UpcomingNotification

.. rubric:: data-types: Retail

`edutap.wallet_google.models.datatypes.retail`

.. currentmodule:: edutap.wallet_google.models.datatypes.retail

.. autosummary::
   :toctree: _autosummary

   DiscoverableProgramMerchantSignupInfo
   DiscoverableProgramMerchantSigninInfo
   DiscoverableProgram

.. rubric:: data-types: Reviews

`edutap.wallet_google.models.datatypes.review`

.. currentmodule:: edutap.wallet_google.models.datatypes.review

.. autosummary::
   :toctree: _autosummary

   Review

.. rubric:: data-types: Smarttap

`edutap.wallet_google.models.datatypes.smarttap`

.. currentmodule:: edutap.wallet_google.models.datatypes.smarttap

.. autosummary::
   :toctree: _autosummary

   Permission
   AuthenticationKey
   SignUpInfo
   IssuerToUserInfo
   IssuerContactInfo
   SmartTapMerchantData

```

## Modules

```{eval-rst}

.. rubric:: Model Registry

`edutap.wallet_google.registry`

.. currentmodule:: edutap.wallet_google.registry

.. autosummary::
   :toctree: _autosummary

   register_model
   lookup_model_by_name
   lookup_model_by_plural_name
   lookup_metadata_by_name
   lookup_metadata_by_model_instance
   lookup_metadata_by_model_type
   raise_when_operation_not_allowed
   RegistryMetadataDict


.. rubric:: HTTP Client Pool

`edutap.wallet_google.clientpool`

HTTP client pooling is managed using httpx clients with OAuth2 service account authentication.
The ClientPoolManager handles both sync and async operations with persistent, pooled clients.
Clients are cached per credentials set and reused across multiple API calls for optimal performance.

**Cleanup:**

- **Sync clients**: Automatically closed on process exit via atexit handler
- **Async clients**: Must be manually closed before event loop shutdown:

  .. code-block:: python

     from edutap.wallet_google.clientpool import client_pool

     # At application shutdown (in async context)
     await client_pool.aclose_all_clients()

.. currentmodule:: edutap.wallet_google.clientpool

.. autosummary::
   :toctree: _autosummary

   ClientPoolManager
   client_pool


.. rubric:: Settings

`edutap.wallet_google.settings`

.. currentmodule:: edutap.wallet_google.settings

.. autosummary::
   :toctree: _autosummary

   Settings
   KubernetesSettings


.. rubric:: Utilities

`edutap.wallet_google.utils`

.. currentmodule:: edutap.wallet_google.utils

.. autosummary::
   :toctree: _autosummary

   encrypt_data
   decrypt_data
   generate_fernet_key
   validate_data
   validate_data_and_convert_to_json
   handle_response_errors
   parse_response_json


.. rubric:: Plugins

`edutap.wallet_google.plugins`

.. currentmodule:: edutap.wallet_google.plugins

.. autosummary::
   :toctree: _autosummary

   register_callback_handler
   get_callback_handlers
   register_image_provider
   get_image_providers


.. rubric:: Protocols

`edutap.wallet_google.protocols`

.. currentmodule:: edutap.wallet_google.protocols

.. autosummary::
   :toctree: _autosummary

   CallbackHandler
   ImageProvider

```

## Exceptions

```{eval-rst}

`edutap.wallet_google.exceptions`

.. currentmodule:: edutap.wallet_google.exceptions

.. autosummary::
   :toctree: _autosummary

   WalletException
   ObjectAlreadyExistsException
   QuotaExceededException

```

## Handlers

### FastAPI Integration

```{eval-rst}

`edutap.wallet_google.handlers.fastapi`

.. currentmodule:: edutap.wallet_google.handlers.fastapi

.. autosummary::
   :toctree: _autosummary

   router_callback
   handle_callback
   router_images
   handle_image

```

### Signature Validation

```{eval-rst}

`edutap.wallet_google.handlers.validate`

.. currentmodule:: edutap.wallet_google.handlers.validate

.. autosummary::
   :toctree: _autosummary

   google_root_signing_public_keys
   verified_signed_message

```
