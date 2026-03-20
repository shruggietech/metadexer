"""Unit tests for SyncPipeline (§7.2)."""

import pytest

from metadexer.catalog import SearchQuery
from metadexer.catalog.backends.sqlite import SqliteCatalogBackend
from metadexer.catalog.ingest import CatalogIngestor
from metadexer.config import StorageRoutingConfig
from metadexer.sync.pipeline import SyncPipeline, SyncResult
from metadexer.vault.backends.local import LocalVaultBackend
from metadexer.vault.inline import VaultInlineStore
from metadexer.vault.store import VaultStore


def _make_raw_entry(
    entry_id="abc123def456",
    mime_type="text/plain",
    size_bytes=42,
    source_path=None,
    inline_content=None,
    **overrides,
):
    """Build a minimal valid IndexEntry dict."""
    entry = {
        "id": entry_id,
        "schema_version": 2,
        "type": "file",
        "mime_type": mime_type,
        "extension": "txt",
        "name": {"text": "hello.txt"},
        "size": {"bytes": size_bytes},
        "timestamps": {
            "modified": {"iso": "2026-01-15T10:30:00+00:00"},
            "created": {"iso": "2026-01-01T00:00:00+00:00"},
        },
        "attributes": {"storage_name": f"{entry_id}.txt"},
    }
    if source_path is not None:
        entry["source_path"] = str(source_path)
    if inline_content is not None:
        entry["inline_content"] = inline_content
    entry.update(overrides)
    return entry


@pytest.fixture()
def pipeline_env(tmp_path):
    """Set up a full pipeline environment with real local backends."""
    vault_root = tmp_path / "vault"
    db_path = tmp_path / "catalog.db"

    # Catalog backend
    catalog_backend = SqliteCatalogBackend(db_path)
    catalog_backend.initialize_schema()

    # Vault inline store (co-located with catalog db)
    inline_store = VaultInlineStore.from_sqlite(catalog_backend.connection)
    inline_store.initialize_schema()

    # Vault file backend
    file_backend = LocalVaultBackend(root=vault_root)

    # VaultStore combining both surfaces
    vault = VaultStore(backend=file_backend, inline_store=inline_store)

    # Ingestor
    ingestor = CatalogIngestor(catalog_backend)

    # Default routing config
    routing_config = StorageRoutingConfig()

    return {
        "vault": vault,
        "ingestor": ingestor,
        "catalog_backend": catalog_backend,
        "inline_store": inline_store,
        "routing_config": routing_config,
        "tmp_path": tmp_path,
    }


def _mock_index_fn(entries):
    """Return a mock indexer function that yields predetermined entries."""

    def _index(target):
        return entries

    return _index


class TestEndToEnd:
    def test_ingest_file_routed(self, pipeline_env, tmp_path):
        """End-to-end ingest: file stored in vault, metadata in catalog."""
        source = tmp_path / "sample.bin"
        source.write_bytes(b"binary content here")

        entry = _make_raw_entry(
            entry_id="file001",
            mime_type="image/jpeg",
            size_bytes=19,
            source_path=source,
        )

        pipeline = SyncPipeline(
            vault=pipeline_env["vault"],
            ingestor=pipeline_env["ingestor"],
            routing_config=pipeline_env["routing_config"],
            index_fn=_mock_index_fn([entry]),
        )

        result = pipeline.ingest(tmp_path)

        assert result.indexed == 1
        assert result.new_vault == 1
        assert result.new_inline == 0
        assert result.duplicate == 0
        assert result.failed == 0
        assert result.errors == ()

        # Verify metadata is in catalog
        record = pipeline_env["catalog_backend"].get_by_id("file001")
        assert record is not None
        assert record.storage_mode == "vault"

        # Verify file is in vault
        assert pipeline_env["vault"].head("file001.txt")

    def test_duplicate_entry_skipped(self, pipeline_env, tmp_path):
        """Duplicate entry yields duplicate count, no errors."""
        source = tmp_path / "dup.txt"
        source.write_text("duplicate text", encoding="utf-8")

        entry = _make_raw_entry(
            entry_id="dup001",
            mime_type="image/png",
            size_bytes=14,
            source_path=source,
        )

        pipeline = SyncPipeline(
            vault=pipeline_env["vault"],
            ingestor=pipeline_env["ingestor"],
            routing_config=pipeline_env["routing_config"],
            index_fn=_mock_index_fn([entry]),
        )

        result1 = pipeline.ingest(tmp_path)
        assert result1.new_vault == 1

        result2 = pipeline.ingest(tmp_path)
        assert result2.duplicate == 1
        assert result2.new_vault == 0
        assert result2.failed == 0

    def test_multiple_entries(self, pipeline_env, tmp_path):
        """Multiple entries processed in a single pipeline run."""
        entries = []
        for i in range(3):
            source = tmp_path / f"file{i}.bin"
            source.write_bytes(f"content-{i}".encode())
            entries.append(
                _make_raw_entry(
                    entry_id=f"multi{i:03d}",
                    mime_type="application/octet-stream",
                    size_bytes=len(f"content-{i}"),
                    source_path=source,
                )
            )

        pipeline = SyncPipeline(
            vault=pipeline_env["vault"],
            ingestor=pipeline_env["ingestor"],
            routing_config=pipeline_env["routing_config"],
            index_fn=_mock_index_fn(entries),
        )

        result = pipeline.ingest(tmp_path)
        assert result.indexed == 3
        assert result.new_vault == 3
        assert result.duplicate == 0
        assert result.failed == 0

    def test_failed_entry_recorded(self, pipeline_env, tmp_path):
        """Entry with bad schema_version recorded as failure."""
        entry = _make_raw_entry(entry_id="bad001")
        entry["schema_version"] = 99

        pipeline = SyncPipeline(
            vault=pipeline_env["vault"],
            ingestor=pipeline_env["ingestor"],
            routing_config=pipeline_env["routing_config"],
            index_fn=_mock_index_fn([entry]),
        )

        result = pipeline.ingest(tmp_path)
        assert result.failed == 1
        assert len(result.errors) == 1
        assert result.errors[0][0] == "bad001"

    def test_inline_routing_stores_in_vault_inline_surface(self, pipeline_env, tmp_path):
        """Inline-routed content stored via VaultInlineStore, FTS searchable."""
        source = tmp_path / "inline.txt"
        source.write_text("hello world searchable text", encoding="utf-8")

        entry = _make_raw_entry(
            entry_id="inl001",
            mime_type="text/plain",
            size_bytes=27,
            source_path=source,
        )

        pipeline = SyncPipeline(
            vault=pipeline_env["vault"],
            ingestor=pipeline_env["ingestor"],
            routing_config=pipeline_env["routing_config"],
            index_fn=_mock_index_fn([entry]),
        )

        result = pipeline.ingest(tmp_path)
        assert result.new_inline == 1
        assert result.new_vault == 0

        # Verify content in vault inline store
        stored = pipeline_env["inline_store"].get("inl001.txt")
        assert "hello world searchable text" in stored

        # Verify FTS search finds it
        search_result = pipeline_env["catalog_backend"].search(SearchQuery(text_query="searchable"))
        assert search_result.total == 1
        assert search_result.items[0].id == "inl001"

    def test_file_routing_stores_in_vault_file_backend(self, pipeline_env, tmp_path):
        """File-routed content yields new_vault == 1."""
        source = tmp_path / "binary.dat"
        source.write_bytes(b"\x00\x01\x02binary")

        entry = _make_raw_entry(
            entry_id="vault001",
            mime_type="application/octet-stream",
            size_bytes=9,
            source_path=source,
        )

        pipeline = SyncPipeline(
            vault=pipeline_env["vault"],
            ingestor=pipeline_env["ingestor"],
            routing_config=pipeline_env["routing_config"],
            index_fn=_mock_index_fn([entry]),
        )

        result = pipeline.ingest(tmp_path)
        assert result.new_vault == 1
        assert result.new_inline == 0

    def test_inline_content_not_in_catalog_assets_table(self, pipeline_env, tmp_path):
        """The assets table has no inline_content column or value."""
        source = tmp_path / "text.txt"
        source.write_text("some text content", encoding="utf-8")

        entry = _make_raw_entry(
            entry_id="check001",
            mime_type="text/plain",
            size_bytes=17,
            source_path=source,
        )

        pipeline = SyncPipeline(
            vault=pipeline_env["vault"],
            ingestor=pipeline_env["ingestor"],
            routing_config=pipeline_env["routing_config"],
            index_fn=_mock_index_fn([entry]),
        )

        pipeline.ingest(tmp_path)

        # Query the assets table directly to verify no inline_content column
        conn = pipeline_env["catalog_backend"].connection
        cursor = conn.execute("PRAGMA table_info(assets)")
        columns = [row[1] for row in cursor.fetchall()]
        assert "inline_content" not in columns


class TestSyncResultFrozen:
    def test_result_is_frozen(self):
        result = SyncResult(
            indexed=1,
            new_vault=1,
            new_inline=0,
            duplicate=0,
            failed=0,
            errors=(),
        )
        with pytest.raises(AttributeError):
            result.indexed = 99  # type: ignore[misc]
