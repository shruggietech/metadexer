"""Catalog database backend implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    from metadexer.catalog import AssetRecord, SearchQuery, SearchResult

__all__ = ["CatalogBackend"]


class CatalogBackend(ABC):
    """Abstract interface for catalog database backends."""

    @abstractmethod
    def initialize_schema(self) -> None:
        """Create the assets table, indexes, and (for SQLite) the FTS5
        virtual table if they do not already exist.

        Implementations MUST be idempotent: calling this method on a
        database that already has the schema is a no-op.
        """

    @abstractmethod
    def upsert_asset(self, record: AssetRecord, search_text: str | None = None) -> bool:
        """Insert an asset record or silently skip if the id already exists.

        Returns True if a new row was inserted, False if the id already
        existed (duplicate ingest). Implementations MUST NOT update
        existing rows on duplicate id; the original record is preserved.

        The search_text parameter, when provided, contains text content
        for full-text search index construction. The backend uses it to
        populate the FTS5 index (SQLite) or search_vector column
        (PostgreSQL) at INSERT time but does NOT store it in a dedicated
        column.
        """

    @abstractmethod
    def get_by_id(self, asset_id: str) -> AssetRecord | None:
        """Return the asset with the given id, or None if not found."""

    @abstractmethod
    def get_by_storage_name(self, storage_name: str) -> AssetRecord | None:
        """Return the asset with the given storage_name, or None if not found."""

    @abstractmethod
    def search(self, query: SearchQuery) -> SearchResult:
        """Execute a search against the assets table.

        The backend translates the SearchQuery into native SQL. Full-text
        search uses SQLite FTS5 or PostgreSQL tsvector/tsquery as
        appropriate. Backends MUST return SearchResult.total as the count
        of all matching rows (ignoring limit/offset) to support pagination.
        """

    @abstractmethod
    def count(self) -> int:
        """Return the total number of assets in the catalog."""

    @abstractmethod
    def iter_all_storage_names(self) -> Iterator[str]:
        """Yield every storage_name in the assets table.

        Used by catalog reconciliation to compare catalog contents
        against vault contents.
        """

    @abstractmethod
    def close(self) -> None:
        """Release database connections and associated resources.

        Implementations MUST be safe to call multiple times.
        """
