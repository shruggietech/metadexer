"""Exception hierarchy for metadexer (§9.3)."""

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
]


class MetadexerError(Exception):
    """Base class for all metadexer exceptions."""


class ConfigurationError(MetadexerError):
    """Configuration is invalid or incomplete.

    Raised when:
    - A TOML configuration file contains syntax errors.
    - A required configuration value is missing (e.g., vault.root not set
      when the local backend is selected).
    - A configuration value has the wrong type or fails validation.
    - An environment variable required for credential resolution is not set
      when the corresponding backend is in use.
    """


# ── Vault exceptions ───────────────────────────────────────────────────────


class VaultError(MetadexerError):
    """Base class for vault module exceptions."""


class VaultObjectNotFoundError(VaultError):
    """A storage_name does not exist in the vault backend.

    Raised by VaultBackend.get, VaultBackend.delete, and
    VaultBackend.open_read when the requested object is absent.
    Propagated by VaultStore.get, VaultStore.verify, and
    VaultStore.prune (for individual deletion failures).
    """


class VaultHashCollisionError(VaultError):
    """A storage_name already exists with different content.

    This indicates that two distinct byte sequences produced the same
    content-derived storage_name. This is a hash collision and represents
    a data integrity violation. This exception is raised during explicit
    verification (VaultStore.verify), not during put (which uses
    head-then-write deduplication without content comparison).
    """


class VaultIOError(VaultError):
    """An I/O operation on the vault backend failed.

    Raised when the underlying storage system reports an error: file
    permission denied, disk full, S3 transport error, network timeout,
    or any other backend-specific I/O failure that is not a missing
    object (which is VaultObjectNotFoundError). The original exception
    is chained as the __cause__ for diagnostic purposes.
    """


# ── Catalog exceptions ─────────────────────────────────────────────────────


class CatalogError(MetadexerError):
    """Base class for catalog module exceptions."""


class CatalogIngestError(CatalogError):
    """An IndexEntry failed validation during catalog ingestion.

    Raised when:
    - schema_version is not 2.
    - A required IndexEntry field is missing or has the wrong type.
    - An IndexEntry cannot be projected into an AssetRecord due to
      structural issues in the raw entry dict.

    The error message includes the asset id (if available) and a
    description of the validation failure.
    """


class CatalogConnectionError(CatalogError):
    """The catalog database is unreachable or authentication failed.

    Raised by backend constructors or on first query when the database
    connection cannot be established. For PostgreSQL: connection refused,
    authentication failure, database does not exist. For SQLite: database
    file path is not writable, file is locked by another process.
    The original driver exception is chained as __cause__.
    """


class CatalogSchemaError(CatalogError):
    """Schema initialization or validation failed.

    Raised by CatalogBackend.initialize_schema when the CREATE TABLE
    or CREATE INDEX statements fail, or when an existing schema is
    detected that is incompatible with the expected structure.
    """


# ── Sync exceptions ────────────────────────────────────────────────────────


class SyncError(MetadexerError):
    """Base class for sync module exceptions."""


class IndexerInvocationError(SyncError):
    """shruggie-indexer invocation failed.

    Raised when the sync module cannot obtain IndexEntry records from
    the indexer. For library-mode invocation: the index_path() call
    raised an exception. For subprocess-mode invocation: the process
    returned a non-zero exit code or produced unparseable output. The
    original exception or process stderr is chained or included in
    the message.
    """


class SyncPipelineError(SyncError):
    """An unrecoverable error occurred during pipeline execution.

    Raised for pipeline-level failures that are not attributable to a
    single component: for example, the vault is unreachable AND the
    catalog is unreachable simultaneously, or a batch operation fails
    in a way that leaves the pipeline in an unrecoverable state. This
    is distinct from per-item failures (which are recorded in results
    and do not raise exceptions) and from component-specific errors
    (which use VaultError or CatalogError subtypes).
    """
