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

### Sync and Async Support

Both synchronous and asynchronous implementations are available:

```python
from edutap.wallet_google.handlers.validate import (
    verified_signed_message,           # Sync
    verified_signed_message_async,     # Async
)

# Sync usage
message = verified_signed_message(callback_data)

# Async usage
message = await verified_signed_message_async(callback_data)
```

### Configuration for Testing

For development and testing, verification can be controlled via environment variables:

- `EDUTAP_WALLET_GOOGLE_HANDLER_CALLBACK_VERIFY_SIGNATURE="0"` - Disables all signature verification
- `EDUTAP_WALLET_GOOGLE_HANDLER_CALLBACK_VERIFY_EXPIRY="0"` - Allows expired messages and keys

These settings enable testing with expired test data without regenerating signatures.

**Important:** Never disable signature verification in production environments.

## Contributing

The sources are in a Git version control system with its main branches at [GitHub](https://github.com/edutap-eu/edutap.wallet_google).

We'd be happy to see many issues, forks, and pull-requests to make this package even better.

Please report any issues at our [issue tracker](https://github.com/edutap-eu/edutap.wallet_google/issues).


## License

The code is under [European Union Public Licence v1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12) (EUPL).
The EUPL is an [OpenSource Initiative (OSI) approved Free and OpenSource license](https://opensource.org/license/eupl-1-2/).
