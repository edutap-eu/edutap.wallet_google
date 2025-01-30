# Installation and Configuration

## Preconditions

Python 3.10+, currently up to 3.13 is tested.
Version 3.13 is recommended.

## Installation

The package is hosted at the Python Package Index (PyPI) and can be installed using `pip install edutap.wallet_google`.

We recommend working with `uv`

```bash
uv venv -p 3.13.0
source .venv/bin/activate
uv pip install edutap.wallet_google
```

## Configuration

Configuration is done using environment variables.

If available, dotenv-files (`.env`) are respected.

### How to connect with Google

In order to create new Wallet Classes and Wallet Objects you need to have a Google Developer account and a Google Wallet API project.

To authenticate with the Google API, you need to provide a credentials file and an issuer ID.

To get the file and the issuer ID, follow the Steps 1 to 4 at [Google Developer instructions for Wallet API access](https://developers.google.com/wallet/generic/web/prerequisites).

In the process you will download a JSON file with the credentials.
It is expected in the filesystem, readable by the program.

In the process you will get an Issuer ID.
It is displayed in the Google Pay and Wallet Console right beside the heading *Google Wallet API* as *Issuer ID* (the term might be translated to your according to your language settings).
Remember it.

Point the environment variable `EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE` to its location.

Example:

```bash
export EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE=/home/example/google_credential_file.json
```

### Configuration options

Credentials

- `EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE`

  Location of the credentials file

  Default points to a test credentials file with fake credentials.

- `EDUTAP_WALLET_GOOGLE_CREDENTIALS_SCOPES`

  The scope of the credentials.
  Do not change!

  Default: `["https://www.googleapis.com/auth/wallet_object.issuer"]`

- `EDUTAP_WALLET_GOOGLE_TEST_ISSUER_ID`

  Only relevant for tests, it has to match a valid Issuer ID of the certificate.

  Default: empty string


FastAPI handler specific settings.
There are two routers available for callback and images, plus one combined providing both at once:

- `EDUTAP_WALLET_GOOGLE_HANDLER_PREFIX`

  Combined handler prefix.

  Default: `/wallet/google`

- `EDUTAP_WALLET_GOOGLE_HANDLER_PREFIX_CALLBACK`

  Callback handler prefix.

  Default: ``

- `EDUTAP_WALLET_GOOGLE_HANDLER_CALLBACK_TIMEOUT`

  Callback handler timeout.
  If the data-provider does not deliver after this number of seconds, timeout.

  Default: `5.0`

- `EDUTAP_WALLET_GOOGLE_ENVIRONMENT`

  The callback handler verifies the intermediate signing key against either Googles test or production keys.
  See also https://developers.google.com/pay/api/android/guides/resources/payment-data-cryptography#root-signing-keys

  This option defines which key to fetch for validation.

  One out of `production` or `testing`.

  Defaults to `testing`.

- `EDUTAP_WALLET_GOOGLE_HANDLER_PREFIX_IMAGES`

  Images handler prefix.

  Default: ``

- `EDUTAP_WALLET_GOOGLE_HANDLER_IMAGE_CACHE_CONTROL`

  Images handler cache-control header settings.
  Each image is delivered with this value as `Cache-Control` in the HTTP-header.

  See https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control

  Default: `no-cache`

- `EDUTAP_WALLET_GOOGLE_HANDLER_IMAGE_TIMEOUT`

  Images handler timeout.
  If the data-provider does not deliver after this number of seconds, timeout.

  Default: `5.0`

- `EDUTAP_WALLET_GOOGLE_FERNET_ENCRYPTIONS_KEY`

  Image Identifiers in the images handler are encrypted symmetrically.
  To generate key use the provided script `generate-fernet-key` or any tool to generate a Fernet key,

  Required if the images handler is used.

  Default: empty string

Google API URLs, normally not subject of change:

- `EDUTAP_WALLET_GOOGLE_API_URL`

  Defaults to `https://walletobjects.googleapis.com/walletobjects/v1`.

- `EDUTAP_WALLET_GOOGLE_SAVE_URL`

  Defaults to `https://pay.google.com/gp/v/save`.

## Development

### Running the tests

Copy the value of the above remembered Issuer Id and point the environment variable `EDUTAP_WALLET_GOOGLE_TEST_ISSUER_ID` to it. Example:

```bash
export EDUTAP_WALLET_GOOGLE_TEST_ISSUER_ID=1234567890123456789
```

In a clone of the repository:

Run unit tests:

```bash
uvx --with tox-uv tox -e test
```

Run integration tests:

```bash
uvx --with tox-uv tox -e test -- --run-integration
```

Format code and run checks:

```bash
uvx --with tox-uv tox -e lint
```

### Debugging

The traffic from and to Google can be logged to a file.
If the environment variable `EDUTAP_WALLET_GOOGLE_RECORD_API_CALLS_DIR` is set to a writeable directory, all traffic is recorded there.
This works also in non-testing environments.
