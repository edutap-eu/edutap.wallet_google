# Reference

## API Functions

Most tasks are done by import and using the `api` module for synchronous operations or `api_async` for asynchronous operations:

```python
from edutap.wallet_google import api
# or for async:
from edutap.wallet_google import api_async
```

To tell the API functions what kind of item to deal with, the first parameter is the registered name of the model (except for `save_link`).
Models can be the different top-level wallet-classes or -objects, but also issuers, permissions and such (see section models below).

### Synchronous API

The synchronous API uses context managers for proper resource cleanup.
All API functions (create, read, update, message, listing) automatically handle session lifecycle using httpx clients with connection pooling.

```{eval-rst}
.. currentmodule:: edutap.wallet_google.api


.. autosummary::
   :toctree: _autosummary

   new
   create
   read
   update
   message
   listing
   save_link
```

### Asynchronous API

The async API provides the same functionality as the synchronous API but uses `async`/`await` for non-blocking I/O operations.
Use this when working with async frameworks like FastAPI or when making concurrent API calls.

```{eval-rst}
.. currentmodule:: edutap.wallet_google.api_async


.. autosummary::
   :toctree: _autosummary

   new
   create
   read
   update
   message
   listing
```

**Note:** `save_link` is only implemented as a synchronous function due to its use of synchronous JWT signing. While it is callable via `api_async`, it executes synchronously and should not be awaited.

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


.. rubric:: Session

`edutap.wallet_google.session`

Sessions are managed using httpx clients with OAuth2 service account authentication.
The SessionManager creates fresh client instances on each call, leveraging httpx's built-in connection pooling for efficiency.
All sessions should be used as context managers for proper resource cleanup.

.. currentmodule:: edutap.wallet_google.session

.. autosummary::
   :toctree: _autosummary

   SessionManager
   HTTPRecorder


.. rubric:: Async Session

`edutap.wallet_google.session_async`

.. currentmodule:: edutap.wallet_google.session_async

.. autosummary::
   :toctree: _autosummary

   AsyncSessionManager


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
   router_image
   get_image

```

### Signature Validation

```{eval-rst}

`edutap.wallet_google.handlers.validate`

.. currentmodule:: edutap.wallet_google.handlers.validate

.. autosummary::
   :toctree: _autosummary

   google_root_signing_public_keys
   verified_signed_message
   google_root_signing_public_keys_async
   verified_signed_message_async

```
