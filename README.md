# edutap.wallet_google

[![PyPI - Version](https://img.shields.io/pypi/v/edutap.wallet_google?logo=python)](https://pypi.org/project/edutap.wallet-google/)
[![CI Tests](https://github.com/edutap-eu/edutap.wallet_google/actions/workflows/tests.yaml/badge.svg)](https://github.com/edutap-eu/edutap.wallet_google/actions/workflows/tests.yaml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/edutap-eu/edutap.wallet_google/main.svg)](https://results.pre-commit.ci/latest/github/edutap-eu/edutap.wallet_google/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Python library for creating and managing digital passes in Google Wallet.**

Digital passes are mobile tickets, membership cards, event tickets, loyalty cards, or coupons that users store in their smartphone's Google Wallet app—like a digital version of the cards in your physical wallet.

## What This Library Does

This package lets you:

- **Create** digital passes (event tickets, membership cards, loyalty cards, etc.)
- **Update** passes already in users' wallets
- **Send** notifications to pass holders
- **List** and manage your issued passes
- **Handle** callbacks when users save or delete passes

**Both sync and async APIs** are supported out of the box.

## Quick Start

```bash
pip install edutap.wallet_google
```

```python
from edutap.wallet_google import api

# Create a pass class (template)
my_class = api.new("GenericClass", {
    "id": "your-issuer-id.your-class-name",
    "classTemplateInfo": {"cardTemplateOverride": {"cardRowTemplateInfos": [...]}}
})
api.create(my_class)

# Create a pass object (the actual pass)
my_pass = api.new("GenericObject", {
    "id": "your-issuer-id.unique-pass-id",
    "classId": "your-issuer-id.your-class-name",
    "state": "ACTIVE"
})
api.create(my_pass)

# Generate "Add to Google Wallet" link
link = api.save_link([my_pass])
```

## Documentation

**[Complete Documentation](https://docs.edutap.eu/packages/edutap_wallet_google/index.html)**

## Features

- **Complete Google Wallet API coverage** - All pass types supported
- **Type-safe** - Full Pydantic models matching Google's schema
- **Sync + Async** - Use the API style that fits your application
- **FastAPI integration** - Ready-made endpoints for callbacks and images
- **Signature verification** - Cryptographic validation of Google's callbacks
- **Modern Python** - Built with httpx, Pydantic v2, and Python 3.10+

## Requirements

- Python 3.10 or later (3.13 recommended)
- Google Cloud Project with Google Wallet API enabled
- Service account credentials (see [documentation](https://docs.edutap.eu/packages/edutap_wallet_google/installation.html))

## License

[EUPL 1.2](https://opensource.org/license/eupl-1-2/) (European Union Public Licence)

## Credits

Developed by the **eduTAP - EUGLOH Working Package - Campus Life** team:

- **Alexander Loechel** (LMU München) - Vision & consulting
- **Philipp Auersperg-Castell** (BlueDynamics Alliance) - Core implementation
- **Jens Klein** (BlueDynamics Alliance) - API design & testing
- **Robert Niederreiter** (BlueDynamics Alliance) - Plugin architecture
- **Simon Lund** (LMU München) - Maintenance

Initial financing: [LMU München](https://www.lmu.de)

Parts of the refactoring and code modernization were assisted by AI with Claude Code.

**Contributing?** We welcome issues and pull requests at [github.com/edutap-eu/edutap.wallet_google](https://github.com/edutap-eu/edutap.wallet_google)
