"""IndexEntry ingestion into the catalog (§6.4.2)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from metadexer.catalog import AssetRecord, IngestResult
from metadexer.exceptions import CatalogIngestError

if TYPE_CHECKING:
    from metadexer.catalog.backends import CatalogBackend

logger = logging.getLogger(__name__)

__all__ = ["CatalogIngestor"]


class CatalogIngestor:
    """Catalog write-path API. Projects IndexEntry fields and persists assets."""

    def __init__(self, backend: CatalogBackend) -> None:
        """Initialize with a configured catalog backend."""
        self._backend = backend

    def ingest(
        self,
        raw_entry: dict,
        storage_mode: str,
        search_text: str | None = None,
    ) -> bool:
        """Ingest a single IndexEntry into the catalog.

        Parameters:
            raw_entry: The complete IndexEntry as a Python dict.
            storage_mode: "vault" or "inline".
            search_text: Text content for full-text search index construction.

        Returns True if new, False if duplicate.
        Raises CatalogIngestError on validation failure.
        """
        record = self._project(raw_entry, storage_mode)
        return self._backend.upsert_asset(record, search_text)

    def ingest_batch(
        self,
        entries: list[tuple[dict, str, str | None]],
    ) -> IngestResult:
        """Ingest multiple IndexEntries in a single operation.

        Each tuple contains (raw_entry, storage_mode, search_text).
        Individual failures are recorded but do not abort the batch.
        Returns an IngestResult summarizing the operation.
        """
        new = 0
        duplicate = 0
        failed = 0
        errors: list[tuple[str, str]] = []

        for i, (raw_entry, storage_mode, search_text) in enumerate(entries):
            entry_id = str(raw_entry.get("id", f"index:{i}"))
            try:
                is_new = self.ingest(raw_entry, storage_mode, search_text)
                if is_new:
                    new += 1
                else:
                    duplicate += 1
            except CatalogIngestError as exc:
                failed += 1
                errors.append((entry_id, str(exc)))

        return IngestResult(
            new=new,
            duplicate=duplicate,
            failed=failed,
            errors=tuple(errors),
        )

    def _project(self, raw_entry: dict, storage_mode: str) -> AssetRecord:
        """Project IndexEntry fields into an AssetRecord."""
        schema_version = raw_entry.get("schema_version")
        if schema_version != 2:
            raise CatalogIngestError(f"Unsupported schema_version: {schema_version!r} (expected 2)")

        try:
            name_text = raw_entry["name"]["text"]
            name_normalized = name_text.lower()
            size_bytes = raw_entry["size"]["bytes"]
            ts_modified_iso = raw_entry["timestamps"]["modified"]["iso"]
            ts_created_iso = raw_entry["timestamps"]["created"]["iso"]
            storage_name = raw_entry["attributes"]["storage_name"]
        except (KeyError, TypeError) as exc:
            raise CatalogIngestError(f"Missing required field in IndexEntry: {exc}") from exc

        return AssetRecord(
            id=raw_entry["id"],
            schema_version=schema_version,
            type=raw_entry.get("type", "file"),
            mime_type=raw_entry.get("mime_type"),
            extension=raw_entry.get("extension"),
            name_text=name_text,
            name_normalized=name_normalized,
            size_bytes=size_bytes,
            ts_modified=datetime.fromisoformat(ts_modified_iso),
            ts_created=datetime.fromisoformat(ts_created_iso),
            storage_name=storage_name,
            storage_mode=storage_mode,
            raw_entry=raw_entry,
            ingested_at=datetime.now(UTC),
        )
