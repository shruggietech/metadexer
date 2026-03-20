"""End-to-end integration tests for Phase 2 (Sprint 010)."""

import json
import sqlite3
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from metadexer.catalog import SearchQuery
from metadexer.catalog.backends.sqlite import SqliteCatalogBackend
from metadexer.catalog.ingest import CatalogIngestor
from metadexer.catalog.search import CatalogSearcher
from metadexer.cli import main
from metadexer.config import MetadexerConfig
from metadexer.sync.pipeline import SyncPipeline
from metadexer.vault.backends.local import LocalVaultBackend
from metadexer.vault.inline import VaultInlineStore
from metadexer.vault.store import VaultStore


def _make_entry(
    entry_id,
    name,
    mime_type="text/plain",
    size_bytes=10,
    source_path=None,
    extension="txt",
):
    """Build a valid IndexEntry dict for testing."""
    entry = {
        "id": entry_id,
        "schema_version": 2,
        "type": "file",
        "mime_type": mime_type,
        "extension": extension,
        "name": {"text": name},
        "size": {"bytes": size_bytes},
        "timestamps": {
            "modified": {"iso": "2026-01-15T10:30:00+00:00"},
            "created": {"iso": "2026-01-01T00:00:00+00:00"},
        },
        "attributes": {"storage_name": f"SHA256-{entry_id}.{extension}"},
        "hashes": {"sha256": "DEADBEEF" * 8},
    }
    if source_path is not None:
        entry["source_path"] = str(source_path)
    return entry


@pytest.fixture()
def e2e_env(tmp_path):
    """Full end-to-end environment with real backends on tmp_path."""
    vault_root = tmp_path / "vault"
    db_path = tmp_path / "catalog.db"

    catalog_backend = SqliteCatalogBackend(db_path)
    catalog_backend.initialize_schema()

    inline_store = VaultInlineStore.from_sqlite(catalog_backend.connection)
    inline_store.initialize_schema()

    file_backend = LocalVaultBackend(root=vault_root)
    vault = VaultStore(backend=file_backend, inline_store=inline_store)
    ingestor = CatalogIngestor(catalog_backend)
    searcher = CatalogSearcher(catalog_backend)

    return {
        "vault": vault,
        "ingestor": ingestor,
        "searcher": searcher,
        "catalog_backend": catalog_backend,
        "inline_store": inline_store,
        "db_path": db_path,
        "vault_root": vault_root,
        "tmp_path": tmp_path,
    }


def _mock_index_fn(entries):
    def _index(target):
        return entries

    return _index


class TestIngestAndQuery:
    def test_ingest_three_files_and_query(self, e2e_env):
        """Ingest 3 files: text inline, JSON inline, binary vault. Query all."""
        tmp = e2e_env["tmp_path"]

        # Text file -> inline
        txt_file = tmp / "readme.txt"
        txt_file.write_text("hello world documentation", encoding="utf-8")

        # JSON file -> inline
        json_file = tmp / "data.json"
        json_file.write_text('{"key": "value"}', encoding="utf-8")

        # Binary file -> vault
        bin_file = tmp / "image.png"
        bin_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        entries = [
            _make_entry("txt001", "readme.txt", "text/plain", 25, txt_file, "txt"),
            _make_entry("json001", "data.json", "application/json", 16, json_file, "json"),
            _make_entry("img001", "image.png", "image/png", 108, bin_file, "png"),
        ]

        from metadexer.config import StorageRoutingConfig

        pipeline = SyncPipeline(
            vault=e2e_env["vault"],
            ingestor=e2e_env["ingestor"],
            routing_config=StorageRoutingConfig(),
            index_fn=_mock_index_fn(entries),
        )

        result = pipeline.ingest(tmp)

        assert result.indexed == 3
        assert result.new_inline == 2  # text + json
        assert result.new_vault == 1  # image
        assert result.failed == 0

        # Text file inline in vault
        content = e2e_env["inline_store"].get("SHA256-txt001.txt")
        assert "hello world documentation" in content

        # FTS finds inline content
        search_result = e2e_env["searcher"].search(SearchQuery(text_query="documentation"))
        assert search_result.total == 1
        assert search_result.items[0].id == "txt001"

        # All 3 assets in catalog
        all_results = e2e_env["searcher"].search(SearchQuery())
        assert all_results.total == 3


class TestDeduplication:
    def test_deduplication_across_runs(self, e2e_env):
        """Second ingest of same entries yields all duplicates."""
        tmp = e2e_env["tmp_path"]
        source = tmp / "file.txt"
        source.write_text("content", encoding="utf-8")
        entries = [_make_entry("dup001", "file.txt", "text/plain", 7, source)]

        from metadexer.config import StorageRoutingConfig

        pipeline = SyncPipeline(
            vault=e2e_env["vault"],
            ingestor=e2e_env["ingestor"],
            routing_config=StorageRoutingConfig(),
            index_fn=_mock_index_fn(entries),
        )

        r1 = pipeline.ingest(tmp)
        assert r1.new_inline == 1

        r2 = pipeline.ingest(tmp)
        assert r2.duplicate == 1
        assert r2.new_inline == 0
        assert r2.new_vault == 0


class TestSearchFilters:
    def test_search_filters_end_to_end(self, e2e_env):
        """Search filters work correctly through the full stack."""
        tmp = e2e_env["tmp_path"]

        txt = tmp / "doc.txt"
        txt.write_text("text content", encoding="utf-8")
        img = tmp / "photo.jpg"
        img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 50)

        entries = [
            _make_entry("f001", "doc.txt", "text/plain", 12, txt, "txt"),
            _make_entry("f002", "photo.jpg", "image/jpeg", 53, img, "jpg"),
        ]

        from metadexer.config import StorageRoutingConfig

        pipeline = SyncPipeline(
            vault=e2e_env["vault"],
            ingestor=e2e_env["ingestor"],
            routing_config=StorageRoutingConfig(),
            index_fn=_mock_index_fn(entries),
        )
        pipeline.ingest(tmp)

        # Filter by MIME type
        result = e2e_env["searcher"].search(SearchQuery(mime_type="image/jpeg"))
        assert result.total == 1
        assert result.items[0].id == "f002"

        # Filter by extension
        result = e2e_env["searcher"].search(SearchQuery(extension="txt"))
        assert result.total == 1
        assert result.items[0].id == "f001"


class TestVaultVerify:
    def test_vault_verify_after_ingest(self, e2e_env):
        """Vault verify passes for correctly stored file content."""
        import hashlib

        tmp = e2e_env["tmp_path"]
        source = tmp / "verify_me.bin"
        data = b"known content for verification"
        source.write_bytes(data)

        expected_sha256 = hashlib.sha256(data).hexdigest().upper()

        entry = _make_entry(
            "ver001",
            "verify_me.bin",
            "application/octet-stream",
            len(data),
            source,
            "bin",
        )
        entry["hashes"] = {"sha256": expected_sha256}

        from metadexer.config import StorageRoutingConfig

        pipeline = SyncPipeline(
            vault=e2e_env["vault"],
            ingestor=e2e_env["ingestor"],
            routing_config=StorageRoutingConfig(),
            index_fn=_mock_index_fn([entry]),
        )
        pipeline.ingest(tmp)

        result = e2e_env["vault"].verify(
            "SHA256-ver001.bin",
            {"sha256": expected_sha256},
        )
        assert result.passed is True


class TestConfigShow:
    def test_config_show_outputs_valid_json(self):
        """config show outputs valid JSON with expected sections."""
        runner = CliRunner()

        with patch("metadexer.cli.load_config") as mock_load:
            mock_load.return_value = MetadexerConfig()
            result = runner.invoke(main, ["config", "show"])

        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert "vault" in parsed
        assert "catalog" in parsed
        assert "storage_routing" in parsed
        assert "logging" in parsed
        assert parsed["vault"]["backend"] == "local"


class TestExitCodes:
    def test_exit_code_on_catalog_error(self):
        """CatalogError maps to exit code 4."""
        from metadexer.exceptions import CatalogConnectionError

        runner = CliRunner()

        with patch("metadexer.cli.load_config") as mock_load:
            mock_load.side_effect = CatalogConnectionError("no database")
            result = runner.invoke(main, ["config", "show"])

        # The exception is a CatalogError subtype -> exit 4
        assert result.exit_code == 4


class TestInlineContentNotInCatalog:
    def test_inline_content_not_in_catalog_assets_table(self, e2e_env):
        """The assets table has no inline_content column; vault_inline has the content."""
        tmp = e2e_env["tmp_path"]
        source = tmp / "inline_check.txt"
        source.write_text("inline text here", encoding="utf-8")

        entries = [_make_entry("ic001", "inline_check.txt", "text/plain", 16, source)]

        from metadexer.config import StorageRoutingConfig

        pipeline = SyncPipeline(
            vault=e2e_env["vault"],
            ingestor=e2e_env["ingestor"],
            routing_config=StorageRoutingConfig(),
            index_fn=_mock_index_fn(entries),
        )
        pipeline.ingest(tmp)

        # Open SQLite directly and verify schema
        conn = sqlite3.connect(str(e2e_env["db_path"]))
        cursor = conn.execute("PRAGMA table_info(assets)")
        column_names = [row[1] for row in cursor.fetchall()]
        assert "inline_content" not in column_names

        # Verify vault_inline table has the content
        cursor = conn.execute(
            "SELECT content FROM vault_inline WHERE storage_name = ?",
            ("SHA256-ic001.txt",),
        )
        row = cursor.fetchone()
        assert row is not None
        assert "inline text here" in row[0]
        conn.close()
