import pytest


@pytest.fixture
def clean_registry():
    from edutap.google_wallet.registry import _REGISTRY

    OLD_REGISTRY = _REGISTRY.copy()
    _REGISTRY.clear()
    yield _REGISTRY
    _REGISTRY.clear()
    _REGISTRY.update(OLD_REGISTRY)


def test_decorator(clean_registry):
    from edutap.google_wallet.registry import register

    @register("foo")
    class Foo:
        pass

    assert clean_registry == {"foo": Foo}
