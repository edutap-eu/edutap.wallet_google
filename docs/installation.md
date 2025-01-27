# Installation and Configuration

## Preconditions

Python 3.10+, currently up to 3.13 is tested.

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

Point the environment variable `EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE` to its location.

Example:

```bash
export EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE=/home/example/google_credential_file.json
```

In the process you will get an Issuer ID.
It is displayed in the Google Pay and Wallet Console right beside the heading *Google Wallet API* as *Issuer ID* (the term might be translated to your according to your language settings).

Copy the value and point the environment variable `EDUTAP_WALLET_GOOGLE_ISSUER_ID` to it. Example:

```bash
export EDUTAP_WALLET_GOOGLE_ISSUER_ID=1234567890123456789
```

### Debugging

The traffic from and to Google can be logged to a file.
If the environment variable `EDUTAP_WALLET_GOOGLE_RECORD_API_CALLS_DIR` is set to a writeable directory, all traffic is recorded there.

## Development

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
