"""Tests for metadexer exception hierarchy (§9.3)."""

import pytest

from metadexer.exceptions import (
    CatalogConnectionError,
    CatalogError,
    CatalogIngestError,
    CatalogSchemaError,
    ConfigurationError,
    IndexerInvocationError,
    MetadexerError,
    SyncError,
    SyncPipelineError,
    VaultError,
    VaultHashCollisionError,
    VaultIOError,
    VaultObjectNotFoundError,
)

ALL_EXCEPTIONS = [
    MetadexerError,
    ConfigurationError,
    VaultError,
    VaultObjectNotFoundError,
    VaultHashCollisionError,
    VaultIOError,
    CatalogError,
    CatalogIngestError,
    CatalogConnectionError,
    CatalogSchemaError,
    SyncError,
    IndexerInvocationError,
    SyncPipelineError,
]


# ── Hierarchy tests ─────────────────────────────────────────────────────────


class TestHierarchy:
    @pytest.mark.parametrize("exc_cls", ALL_EXCEPTIONS)
    def test_all_are_subclass_of_metadexer_error(self, exc_cls):
        assert issubclass(exc_cls, MetadexerError)

    @pytest.mark.parametrize("exc_cls", [VaultError, CatalogError, SyncError])
    def test_module_bases_are_subclass_of_metadexer_error(self, exc_cls):
        assert issubclass(exc_cls, MetadexerError)

    @pytest.mark.parametrize(
        "leaf, base",
        [
            (VaultObjectNotFoundError, VaultError),
            (VaultHashCollisionError, VaultError),
            (VaultIOError, VaultError),
            (CatalogIngestError, CatalogError),
            (CatalogConnectionError, CatalogError),
            (CatalogSchemaError, CatalogError),
            (IndexerInvocationError, SyncError),
            (SyncPipelineError, SyncError),
        ],
    )
    def test_leaf_exceptions_subclass_module_base(self, leaf, base):
        assert issubclass(leaf, base)
        assert issubclass(leaf, MetadexerError)

    def test_configuration_error_is_direct_subclass(self):
        assert issubclass(ConfigurationError, MetadexerError)
        assert ConfigurationError.__bases__ == (MetadexerError,)


# ── Instantiation tests ────────────────────────────────────────────────────


class TestInstantiation:
    @pytest.mark.parametrize("exc_cls", ALL_EXCEPTIONS)
    def test_instantiation_with_message(self, exc_cls):
        msg = f"test message for {exc_cls.__name__}"
        exc = exc_cls(msg)
        assert str(exc) == msg

    @pytest.mark.parametrize("exc_cls", ALL_EXCEPTIONS)
    def test_catchable_as_exception(self, exc_cls):
        with pytest.raises(exc_cls):
            raise exc_cls("test")


# ── Chaining test ───────────────────────────────────────────────────────────


class TestChaining:
    def test_exception_chaining_preserves_cause(self):
        cause = ValueError("original cause")
        try:
            raise CatalogConnectionError("connection failed") from cause
        except CatalogConnectionError as exc:
            assert exc.__cause__ is cause
            assert isinstance(exc.__cause__, ValueError)
            assert str(exc) == "connection failed"


# ── Re-export tests ─────────────────────────────────────────────────────────


class TestReExports:
    @pytest.mark.parametrize("exc_name", [cls.__name__ for cls in ALL_EXCEPTIONS])
    def test_importable_from_metadexer(self, exc_name):
        import metadexer

        assert hasattr(metadexer, exc_name)
        exc_cls = getattr(metadexer, exc_name)
        assert issubclass(exc_cls, MetadexerError)

    @pytest.mark.parametrize("exc_name", [cls.__name__ for cls in ALL_EXCEPTIONS])
    def test_importable_from_metadexer_exceptions(self, exc_name):
        import metadexer.exceptions

        assert hasattr(metadexer.exceptions, exc_name)
        exc_cls = getattr(metadexer.exceptions, exc_name)
        assert issubclass(exc_cls, MetadexerError)
