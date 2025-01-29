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


## Contributing

The sources are in a Git version control system with its main branches at [GitHub](https://github.com/edutap-eu/edutap.wallet_google).

We'd be happy to see many issues, forks, and pull-requests to make this package even better.

Please report any issues at our [issue tracker](https://github.com/edutap-eu/edutap.wallet_google/issues).


## License

The code is under [European Union Public Licence v1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12) (EUPL).
The EUPL is an [OpenSource Initiative (OSI) approved Free and OpenSource license](https://opensource.org/license/eupl-1-2/).
