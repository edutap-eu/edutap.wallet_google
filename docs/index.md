# `edutap.wallet_google` Package Documentation

A Python library to interact with the Google Wallet Restful API.

It provides an API to
- create, read, update, disable, and list Wallet Classes, Wallet Objects, and related items,
- issue passes.

The package contains validating data-models of the Google data structures made with [Pydantic](https://docs.pydantic.dev/).

Behind the scenes it provides a session manager for authorized HTTPS communication with the Google Restful API.
An extensible registry for additional models of classes and objects ensures extendibility.

The documentation for `edutap.wallet_google` is roughly structured into four parts:

1. How to install and configure the package is covered in Installation.
1. The basic introductions to using the API are covered in the Tutorials.
1. The technical reference to API and the underlying data models within the package are covered in Reference.
   It includes several links to the original Google Wallet Restful API documentation.
1. A general overview how the Google Wallet API works is covered in the Explanation section.

```{toctree}
---
maxdepth: 2
caption: Contents
---

installation
tutorials
reference
explanation

```
