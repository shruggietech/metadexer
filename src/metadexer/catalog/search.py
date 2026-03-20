"""Catalog query interface (§6.4.2)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from metadexer.catalog import AssetRecord, SearchQuery, SearchResult
    from metadexer.catalog.backends import CatalogBackend

logger = logging.getLogger(__name__)

__all__ = ["CatalogSearcher"]


class CatalogSearcher:
    """Catalog read-path API. Builds queries and returns structured results."""

    def __init__(self, backend: CatalogBackend) -> None:
        """Initialize with a configured catalog backend."""
        self._backend = backend

    def search(self, query: SearchQuery) -> SearchResult:
        """Execute a search query against the catalog.

        Delegates to backend.search() after validating the query.
        Returns a SearchResult containing matching AssetRecords and
        a total count for pagination.
        """
        return self._backend.search(query)

    def get(self, asset_id: str) -> AssetRecord | None:
        """Retrieve a single asset by its content-addressed id.

        Delegates to backend.get_by_id(). Returns None if not found.
        """
        return self._backend.get_by_id(asset_id)

    def get_by_storage_name(self, storage_name: str) -> AssetRecord | None:
        """Retrieve a single asset by its vault storage key.

        Delegates to backend.get_by_storage_name(). Returns None if
        not found.
        """
        return self._backend.get_by_storage_name(storage_name)

    def count(self) -> int:
        """Return the total number of assets in the catalog.

        Delegates to backend.count().
        """
        return self._backend.count()
