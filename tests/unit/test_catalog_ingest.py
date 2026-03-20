"""Unit tests for CatalogIngestor (§6.4.2)."""

from datetime import UTC, datetime

import pytest

from metadexer.catalog import SearchQuery
from metadexer.catalog.backends.sqlite import SqliteCatalogBackend
from metadexer.catalog.ingest import CatalogIngestor
from metadexer.exceptions import CatalogIngestError


def _make_raw_entry(**overrides):
    """Build a minimal valid IndexEntry dict."""
    entry = {
        "id": "abc123def456",
        "schema_version": 2,
        "type": "file",
        "mime_type": "text/plain",
        "extension": "txt",
        "name": {"text": "hello.txt"},
        "size": {"bytes": 42},
        "timestamps": {
            "modified": {"iso": "2026-01-15T10:30:00+00:00"},
            "created": {"iso": "2026-01-01T00:00:00+00:00"},
        },
        "attributes": {"storage_name": "abc123def456.txt"},
    }
    entry.update(overrides)
    return entry


@pytest.fixture()
def backend(tmp_path):
    db_path = tmp_path / "catalog.db"
    b = SqliteCatalogBackend(db_path)
    b.initialize_schema()
    yield b
    b.close()


@pytest.fixture()
def ingestor(backend):
    return CatalogIngestor(backend)


class TestIngest:
    def test_valid_entry_returns_true(self, ingestor):
        raw = _make_raw_entry()
        assert ingestor.ingest(raw, "vault") is True

    def test_duplicate_returns_false(self, ingestor):
        raw = _make_raw_entry()
        ingestor.ingest(raw, "vault")
        assert ingestor.ingest(raw, "vault") is False

    def test_projects_fields_correctly(self, ingestor, backend):
        raw = _make_raw_entry()
        ingestor.ingest(raw, "vault")
        record = backend.get_by_id("abc123def456")
        assert record is not None
        assert record.id == "abc123def456"
        assert record.schema_version == 2
        assert record.type == "file"
        assert record.mime_type == "text/plain"
        assert record.extension == "txt"
        assert record.name_text == "hello.txt"
        assert record.name_normalized == "hello.txt"
        assert record.size_bytes == 42
        assert record.ts_modified == datetime(2026, 1, 15, 10, 30, 0, tzinfo=UTC)
        assert record.ts_created == datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
        assert record.storage_name == "abc123def456.txt"
        assert record.storage_mode == "vault"
        assert record.ingested_at is not None

    def test_preserves_raw_entry(self, ingestor, backend):
        raw = _make_raw_entry()
        ingestor.ingest(raw, "vault")
        record = backend.get_by_id("abc123def456")
        assert record.raw_entry == raw

    def test_search_text_populates_fts(self, ingestor, backend):
        raw = _make_raw_entry(
            id="inline1",
            **{"attributes": {"storage_name": "inline1.txt"}},
        )
        ingestor.ingest(raw, "inline", search_text="hello world")
        result = backend.search(SearchQuery(text_query="hello"))
        assert result.total == 1
        assert result.items[0].id == "inline1"

    def test_vault_mode_no_search_text_name_fts(self, ingestor, backend):
        raw = _make_raw_entry(
            id="vault1",
            **{"attributes": {"storage_name": "vault1.txt"}, "name": {"text": "important.txt"}},
        )
        ingestor.ingest(raw, "vault")
        result = backend.search(SearchQuery(text_query="important"))
        assert result.total == 1
        assert result.items[0].id == "vault1"

    def test_rejects_schema_version_not_2(self, ingestor):
        raw = _make_raw_entry(schema_version=1)
        with pytest.raises(CatalogIngestError, match="schema_version"):
            ingestor.ingest(raw, "vault")

    def test_rejects_missing_required_field(self, ingestor):
        raw = _make_raw_entry()
        del raw["name"]
        with pytest.raises(CatalogIngestError, match="Missing required field"):
            ingestor.ingest(raw, "vault")


class TestIngestBatch:
    def test_success(self, ingestor):
        entries = [
            (
                _make_raw_entry(id=f"b{i}", **{"attributes": {"storage_name": f"b{i}.txt"}}),
                "vault",
                None,
            )
            for i in range(3)
        ]
        result = ingestor.ingest_batch(entries)
        assert result.new == 3
        assert result.duplicate == 0
        assert result.failed == 0
        assert result.errors == ()

    def test_with_duplicates(self, ingestor):
        raw = _make_raw_entry()
        ingestor.ingest(raw, "vault")
        entries = [(raw, "vault", None)]
        result = ingestor.ingest_batch(entries)
        assert result.new == 0
        assert result.duplicate == 1
        assert result.failed == 0

    def test_with_failures(self, ingestor):
        bad = _make_raw_entry(schema_version=99)
        entries = [(bad, "vault", None)]
        result = ingestor.ingest_batch(entries)
        assert result.new == 0
        assert result.duplicate == 0
        assert result.failed == 1
        assert len(result.errors) == 1

    def test_mixed(self, ingestor):
        good = _make_raw_entry(id="m1", **{"attributes": {"storage_name": "m1.txt"}})
        bad = _make_raw_entry(
            id="m2", schema_version=99, **{"attributes": {"storage_name": "m2.txt"}}
        )
        dup = _make_raw_entry(id="m1", **{"attributes": {"storage_name": "m1.txt"}})
        entries = [
            (good, "vault", None),
            (bad, "vault", None),
            (dup, "vault", None),
        ]
        result = ingestor.ingest_batch(entries)
        assert result.new == 1
        assert result.duplicate == 1
        assert result.failed == 1
        assert len(result.errors) == 1
