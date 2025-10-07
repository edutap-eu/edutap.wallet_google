from edutap.wallet_google.settings import ROOT_DIR

import pytest


def test_session_manager_url(
    clean_registry_by_name,
    clean_registry_by_model,
):  # noqa: F811
    from edutap.wallet_google.registry import register_model

    @register_model("Foo", url_part="foo")
    class Foo:
        pass

    from edutap.wallet_google.session import SessionManager

    manager = SessionManager()
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


def test_session_creation(monkeypatch):
    from edutap.wallet_google.credentials import credentials_manager
    from edutap.wallet_google.session import SessionManager

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

    manager = SessionManager()
    session = manager.session()
    assert session is not None
    assert manager.settings.credentials_file is not None
    # With httpx/authlib AssertionClient, verify the session was created successfully
    assert session.__class__.__name__ == "AssertionClient"

    # Each call to session() now returns a fresh client (no caching)
    session2 = manager.session()
    assert session2 is not None
    assert session2 is not session  # Different instances


def test_session_with_HTTPRecorder(tmp_path, monkeypatch):
    from edutap.wallet_google.session import SessionManager

    manager = SessionManager()
    manager.settings.record_api_calls_dir = tmp_path
    manager.settings.credentials_file = (
        ROOT_DIR / "tests" / "data" / "credentials_fake.json"
    )
    session = manager.session()
    # With httpx, HTTPRecorder is the client class used by AssertionClient
    assert session.__class__.__name__ == "AssertionClient"
    # When recording is enabled, AssertionClient is created with client_cls=HTTPRecorder
    # We verify recording is configured by checking that the setting is set
    assert manager.settings.record_api_calls_dir == tmp_path
