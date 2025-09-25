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


def test_session_creation(monkeypatch, clean_session_threadlocals):
    from edutap.wallet_google.session import SessionManager

    def mock_get_credentials_providers():
        raise NotImplementedError()

    monkeypatch.setattr(
        "edutap.wallet_google.session.get_credentials_providers",
        mock_get_credentials_providers,
    )

    monkeypatch.setenv(
        "EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE",
        str(ROOT_DIR / "tests" / "data" / "credentials_non_existent.json"),
    )
    with pytest.raises(ValueError):
        SessionManager()._credentials_for_issuer("dummy-issuer")

    monkeypatch.setenv(
        "EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE",
        str(ROOT_DIR / "tests" / "data" / "credentials_fake.json"),
    )

    manager = SessionManager()
    session = manager.session("dummy-issuer")
    assert session is not None
    assert manager.settings.credentials_file is not None
    assert session.credentials.scopes == [
        "https://www.googleapis.com/auth/wallet_object.issuer",
    ]

    from edutap.wallet_google.session import _THREADLOCAL

    assert _THREADLOCAL.sessions["dummy-issuer"] is session

    import threading

    def thread_check_different_session(other_session_id):
        session = manager.session("dummy-issuer")  # noqa: F841
        assert id(_THREADLOCAL.sessions["dummy-issuer"]) != other_session_id

    threading.Thread(target=thread_check_different_session, args=[id(session)]).start()


def test_session_creation_with_provider(monkeypatch, clean_session_threadlocals):
    from edutap.wallet_google.session import SessionManager

    class MockCredentialsProvider:

        def credentials_for_issuer(self, issuer_id: str) -> str:
            with (ROOT_DIR / "tests" / "data" / "credentials_fake.json").open(
                "r"
            ) as fd:
                return fd.read()

    def mock_get_credentials_providers():
        return [MockCredentialsProvider()]

    monkeypatch.setattr(
        "edutap.wallet_google.session.get_credentials_providers",
        mock_get_credentials_providers,
    )

    manager = SessionManager()
    session = manager.session(credentials={
        "private_key_id": "dummy-key-id",
        'client_email': "dummy@tld.net",
        'token_uri': "http://token-uri",
    })
    assert session is not None


def test_session_creation_with_provider_none_found(
    monkeypatch, clean_session_threadlocals
):
    from edutap.wallet_google.session import SessionManager

    class MockCredentialsProvider:

        def credentials_for_issuer(self, issuer_id: str) -> str:
            raise LookupError()

    def mock_get_credentials_providers():
        return [MockCredentialsProvider()]

    monkeypatch.setattr(
        "edutap.wallet_google.session.get_credentials_providers",
        mock_get_credentials_providers,
    )

    manager = SessionManager()

    pytest.raises(LookupError, manager.session, "dummy-issuer")


def test_session_with_HTTPRecorder(tmp_path, monkeypatch):
    from edutap.wallet_google.session import _THREADLOCAL
    from edutap.wallet_google.session import SessionManager

    def mock_get_credentials_providers():
        raise NotImplementedError()

    monkeypatch.setattr(
        "edutap.wallet_google.session.get_credentials_providers",
        mock_get_credentials_providers,
    )

    delattr(_THREADLOCAL, "sessions")
    manager = SessionManager()
    manager.settings.record_api_calls_dir = tmp_path
    manager.settings.credentials_file = (
        ROOT_DIR / "tests" / "data" / "credentials_fake.json"
    )
    session = manager.session("dummy-user")
    assert session.adapters["https://"].__class__.__name__ == "HTTPRecorder"
