# src/metadexer/__init__.py
"""metadexer — Content-addressed asset management."""

from metadexer._version import __version__
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

__all__ = [
    "CatalogConnectionError",
    "CatalogError",
    "CatalogIngestError",
    "CatalogSchemaError",
    "ConfigurationError",
    "IndexerInvocationError",
    "MetadexerError",
    "SyncError",
    "SyncPipelineError",
    "VaultError",
    "VaultHashCollisionError",
    "VaultIOError",
    "VaultObjectNotFoundError",
    "__version__",
]
