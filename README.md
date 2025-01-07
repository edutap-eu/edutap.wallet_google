# edutap.wallet_google

<p style="text-align:center;">

![PyPI - Version](https://img.shields.io/pypi/v/edutap.wallet_google?logo=python)
[![CI Tests](https://github.com/edutap-eu/edutap.wallet_google/actions/workflows/tests.yaml/badge.svg)](https://github.com/edutap-eu/edutap.wallet_google/actions/workflows/tests.yaml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/edutap-eu/edutap.wallet_google/main.svg)](https://results.pre-commit.ci/latest/github/edutap-eu/edutap.wallet_google/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub Repo stars](https://img.shields.io/github/stars/edutap-eu/edutap.wallet_google)

</p>

This package provides a Python API to interact with the Google Wallet Restful API

It contains:

- an API to create, read, update and list wallet classes and objects to issue passes;
- FastAPI endpoints for Google callbacks and pass image delivery.

This is supported by
- Pydantic models of the classes, objects, and their data-types according to the Google documentation;
- an extensible registry for models of these classes and objects;
- a session manager for authorized HTTPS communication with the Google Restful API;
- a plugin system with protocols to decouple the actual business logic for the callback/ image provider.

## Documentation

Read the [complete `edutap.wallet_google` documentation](https://docs.edutap.eu/packages/edutap_wallet_google/index.html) to get started.

## Source Code

The sources are in a GIT DVCS with its main branches at the [GitHub `edutap-eu` `edutap.wallet_google` repository](https://github.com/edutap-eu/edutap.wallet_google) .

We'd be happy to see many issue reports, forks and pull requests to make the package even better.

## Credits

This project was initiated and initially financed by [LMU München](https://www.lmu.de).

Contributors:

- Alexander Loechel (LMU)
- Philipp Auersperg-Castell (BlueDynamics Alliance)
- Jens Klein (BlueDynamics Alliance)

## License

The code is copyrighted by eduTAP - EUGLOH Working Package - Campus Life and contributors.

It is licensed under the [EUROPEAN UNION PUBLIC LICENCE v. 1.2](https://opensource.org/license/eupl-1-2/), a free and OpenSource software license.
