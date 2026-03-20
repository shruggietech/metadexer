"""Catalog module — metadata registry, search, and references."""

from dataclasses import dataclass
from datetime import datetime

__all__ = ["AssetRecord", "IngestResult", "SearchQuery", "SearchResult"]


@dataclass(frozen=True)
class AssetRecord:
    """A single asset as represented in the catalog.

    Used on both the write path (CatalogIngestor builds one from an
    IndexEntry) and the read path (CatalogBackend returns them from
    queries). Field names correspond to the assets table columns
    defined in §6.8.
    """

    id: str
    schema_version: int
    type: str  # "file" or "directory"
    mime_type: str | None
    extension: str | None
    name_text: str | None
    name_normalized: str | None
    size_bytes: int | None
    ts_modified: datetime | None
    ts_created: datetime | None
    storage_name: str
    storage_mode: str  # "vault" or "inline"
    raw_entry: dict  # complete IndexEntry, deserialized
    ingested_at: datetime


@dataclass(frozen=True)
class SearchQuery:
    """Parameters for a catalog search operation.

    All filter fields are optional. When None, the filter is not applied.
    Multiple filters combine with AND logic. An empty SearchQuery (all
    fields None/default) matches all assets.
    """

    text_query: str | None = None  # full-text search string (FTS)
    mime_type: str | None = None  # exact match (e.g., "image/jpeg")
    mime_prefix: str | None = None  # prefix match (e.g., "text/")
    extension: str | None = None  # exact match, no leading dot
    type: str | None = None  # "file" or "directory"
    size_min: int | None = None  # inclusive lower bound on size_bytes
    size_max: int | None = None  # inclusive upper bound on size_bytes
    modified_after: datetime | None = None  # exclusive lower bound on ts_modified
    modified_before: datetime | None = None  # exclusive upper bound on ts_modified
    name_contains: str | None = None  # case-insensitive substring on name_text
    limit: int = 100  # max results to return
    offset: int = 0  # pagination offset


@dataclass(frozen=True)
class SearchResult:
    """Result of a catalog search operation."""

    items: tuple[AssetRecord, ...]  # matching assets for this page
    total: int  # total matches (ignoring limit/offset)
    query: SearchQuery  # the query that produced this result


@dataclass(frozen=True)
class IngestResult:
    """Result of a batch ingest operation."""

    new: int  # count of newly inserted assets
    duplicate: int  # count of assets skipped (already existed)
    failed: int  # count of assets that failed validation
    errors: tuple[tuple[str, str], ...]  # (asset_id_or_index, error_message)
