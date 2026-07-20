# Explanations

## Google Wallet API

The [Google Wallet](https://developers.google.com/wallet/) API is not self explanatory.

The Python API client follows the models and data-structure defined by Google.

- Overall Google defines Wallet Classes which are templates for Wallet Objects, while latter are the actual passes, referencing it's Wallet Class.
- There are different types of Wallet Classes and Wallet Objects, while each type is always a pair of Wallet Class and Wallet Object, i.e. `RetailClass` and `RetailObject`.
  Those are the top-level models.
  Additional, there are supporting top-level objects like `Issuer`, `Permissions`, and more.
- Each Wallet Class or Wallet Object has a set of fields which are defined by Google and can not be changed.
- Each fields type is either a simple value or another data-type with its own fields.

In this client package all data-structure defined by Google are represented by Pydantic models.
The models are defined in the `edutap.wallet_google.models` module and are documented in the [Reference](reference.md).

All top-level models are registered in the `edutap.wallet_google.registry` module.
In further code, the models are referenced by their registered name, which is the name of the class (in CamelCase, as Google names them).

The API functions are defined in the `edutap.wallet_google.api` module.
They follow a CRUD API approach, while there is no delete at Google Wallet (this needs to be done as an update with expiration date in past).
Additional a message can be sent to a Wallet Class or Wallet Object.
Also, a download link aka  "Add To Wallet" link can be created.
All are documented in the [Reference](reference.md) section.

Some API functions do take a name of a model as first parameter.
The name is the registered name.
Depending on the registered name used, a function might not be able to execute.
This is checked by the API function at runtime based on the registry record of the model, where the capabilities are stored.
Each constraint origins in the Google API and is mirrored here.


## Callback Signature Verification

Google Wallet sends signed callbacks when passes are saved, updated, or deleted.
The package includes comprehensive signature verification following Google's ECv2SigningOnly protocol.

### Verification Process

The verification happens in multiple stages:

1. **Fetch Google's Root Signing Keys**: Retrieved from Google's public endpoint and cached with automatic expiration based on key lifetimes
2. **Verify Intermediate Signing Key**: The intermediate key in the callback is verified against Google's root keys
3. **Verify Message Signature**: The callback message signature is verified using the intermediate key
4. **Check Expirations**: Both message and key expiration timestamps are validated

### Async Implementation

The validation functions are async-only (as they're used by the FastAPI handlers):

```python
from edutap.wallet_google.handlers.validate import (
    google_root_signing_public_keys,
    verified_signed_message,
)

# Fetch Google's root signing keys
keys = await google_root_signing_public_keys(google_environment)

# Verify callback message
message = await verified_signed_message(callback_data)
```

### Configuration for Testing

For development and testing, verification can be controlled via environment variables:

- `EDUTAP_WALLET_GOOGLE_HANDLER_CALLBACK_VERIFY_SIGNATURE="0"` - Disables all signature verification
- `EDUTAP_WALLET_GOOGLE_HANDLER_CALLBACK_VERIFY_EXPIRY="0"` - Allows expired messages and keys

These settings enable testing with expired test data without regenerating signatures.

**Important:** Never disable signature verification in production environments.

## Private image or ImageProvider?

The library already offers a way to serve images that are not on a public
CDN: an `ImageProvider` plugin plus the FastAPI `/images/{encrypted_image_id}`
route (see [Reference](reference.md)). That endpoint is reachable by anyone
who has the URL — the id is encrypted, not authenticated. A private image,
uploaded via `api.upload_private_image()`, is never publicly reachable at
all. The trade-offs:

| | `ImageProvider` + public route | private image |
| --- | --- | --- |
| reachable without the pass | yes, if the URL leaks | no |
| usable on classes | yes | no |
| usable for logo / hero image | yes | no |
| reusable across passes | yes | no, one image per object |
| changeable after issuing | yes, same URL new bytes | no, requires re-upload and patch |
| requires a reachable service | yes | no |
| caller must persist anything | no | yes, see below |

### The synchronous bridge to ImageProvider

`upload_private_image_by_id()`, the synchronous variant, obtains the image
from the registered `ImageProvider` plugin by creating and tearing down a
fresh event loop on every call, because `ImageProvider.image_by_id()` is
async by protocol.

This has a consequence for how an `ImageProvider` implementation may hold
onto async resources. An implementation that caches an async resource across
calls — a module-level `httpx.AsyncClient`, for instance — binds that
resource to the event loop that was running when it was created. On the
second call, `upload_private_image_by_id()` runs a *new* loop; the loop the
cached client is bound to is already closed, and the client fails.

Implementations meant to be used with the synchronous bridge must therefore
create their async resources fresh inside every `image_by_id()` call. An
implementation that needs to cache resources across calls should instead be
used through `aupload_private_image_by_id()`, which runs inside the caller's
own event loop and never creates one of its own.

## Lifecycle and the obligation to persist the id

This section carries the warning, because getting it wrong is silent and
unrecoverable:

- The id is returned exactly once. Google offers no endpoint to list an
  issuer's private images.
- There is no delete operation.
- An id may be referenced by one object only; a second object needs a fresh
  upload.

Consequences the caller must act on:

1. **Persist the id together with the object it belongs to, before creating
   the object.** If the process dies between upload and `create()`, the id
   is lost and the image is orphaned at Google forever.
2. **Never retry an upload as part of a `create()` retry.** Upload once, then
   retry only the `create()`. A naive retry loop around both leaks one image
   per attempt.
3. **Re-issuing a pass means re-uploading the image.**

The library deliberately stores nothing. Where the mapping lives — a
relational table, a compacted Kafka topic, anything else — is an application
decision. A minimal relational shape for orientation:

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

A note on event streams: an "image uploaded" event is useful for auditing,
but an event log is not a lookup store. The source of truth for "which id
belongs to this pass" must be queryable by object id.

## Contributing

The sources are in a Git version control system with its main branches at [GitHub](https://github.com/edutap-eu/edutap.wallet_google).

We'd be happy to see many issues, forks, and pull-requests to make this package even better.

Please report any issues at our [issue tracker](https://github.com/edutap-eu/edutap.wallet_google/issues).


## License

The code is under [European Union Public Licence v1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12) (EUPL).
The EUPL is an [OpenSource Initiative (OSI) approved Free and OpenSource license](https://opensource.org/license/eupl-1-2/).
