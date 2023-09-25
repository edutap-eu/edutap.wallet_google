def test_session_manager_url(clean_registry):  # noqa: F811
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
    from edutap.wallet_google.session import SessionManager
    from pathlib import Path

    monkeypatch.setenv(
        "EDUTAP_WALLET_GOOGLE_CREDENTIALS_FILE",
        str(Path(__file__).parent / "data" / "credentials_fake.json"),
    )
    manager = SessionManager()
    session = manager.session
    assert session is not None
    assert session.credentials is not None
    assert session.credentials.scopes == [
        "https://www.googleapis.com/auth/wallet_object.issuer"
    ]

    from edutap.wallet_google.session import _THREADLOCAL

    assert _THREADLOCAL.session is session

    import threading

    def thread_check_different_session(other_session_id):
        session = manager.session  # noqa: F841
        assert id(_THREADLOCAL.session) != other_session_id

    threading.Thread(target=thread_check_different_session, args=[id(session)]).start()
