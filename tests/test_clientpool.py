import pytest

from edutap.wallet_google.settings import ROOT_DIR


def test_client_pool_url(
    clean_registry_by_name,
    clean_registry_by_model,
):  # noqa: F811
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo")
    class Foo:
        pass

    from edutap.wallet_google.clientpool import ClientPoolManager

    manager = ClientPoolManager()
    assert (
        manager.url("Foo")
        == "https://walletobjects.googleapis.com/walletobjects/v1/foo"
    )
    assert (
        manager.url("Foo", "/bar")
        == "https://walletobjects.googleapis.com/walletobjects/v1/foo/bar"
    )

    @register_model("Foo2", url_part="foobar")
    class Foo2:
        pass

    assert (
        manager.url("Foo2")
        == "https://walletobjects.googleapis.com/walletobjects/v1/foobar"
    )
    assert (
        manager.url("Foo2", "/baz")
        == "https://walletobjects.googleapis.com/walletobjects/v1/foobar/baz"
    )


def test_client_creation(monkeypatch):
    from edutap.wallet_google.clientpool import ClientPoolManager
    from edutap.wallet_google.credentials import credentials_manager

    # Clear the cache and settings before testing
    credentials_manager.credentials_from_file.cache_clear()
    if hasattr(credentials_manager, "_settings"):
        delattr(credentials_manager, "_settings")

    monkeypatch.setenv(
        "EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE",
        str(ROOT_DIR / "tests" / "data" / "credentials_non_existent.json"),
    )
    with pytest.raises(ValueError):
        credentials_manager.credentials_from_file()

    # Clear cache and settings again before next test
    credentials_manager.credentials_from_file.cache_clear()
    if hasattr(credentials_manager, "_settings"):
        delattr(credentials_manager, "_settings")

    monkeypatch.setenv(
        "EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE",
        str(ROOT_DIR / "tests" / "data" / "credentials_fake.json"),
    )

    manager = ClientPoolManager()
    client = manager.client()
    assert client is not None
    assert manager.settings.credentials_file is not None
    # With httpx/authlib AssertionClient, verify the client was created successfully
    assert client.__class__.__name__ == "AssertionClient"

    # Each call to client() now returns the SAME cached client (for connection pooling)
    client2 = manager.client()
    assert client2 is not None
    assert client2 is client  # Same instance (cached)
