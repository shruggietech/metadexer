"""Unit tests for CatalogSearcher (§6.4.2)."""

from datetime import UTC, datetime

import pytest

from metadexer.catalog import AssetRecord, SearchQuery
from metadexer.catalog.backends.sqlite import SqliteCatalogBackend
from metadexer.catalog.search import CatalogSearcher


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


def _make_record(**overrides):
    defaults = {
        "id": "abc123def456",
        "schema_version": 2,
        "type": "file",
        "mime_type": "text/plain",
        "extension": "txt",
        "name_text": "hello.txt",
        "name_normalized": "hello.txt",
        "size_bytes": 42,
        "ts_modified": datetime(2026, 1, 15, 10, 30, 0, tzinfo=UTC),
        "ts_created": datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
        "storage_name": "abc123def456.txt",
        "storage_mode": "vault",
        "raw_entry": {"id": "abc123def456", "schema_version": 2},
        "ingested_at": datetime(2026, 3, 19, 12, 0, 0, tzinfo=UTC),
    }
    defaults.update(overrides)
    return AssetRecord(**defaults)


@pytest.fixture()
def backend(tmp_path):
    db_path = tmp_path / "catalog.db"
    b = SqliteCatalogBackend(db_path)
    b.initialize_schema()
    yield b
    b.close()


@pytest.fixture()
def searcher(backend):
    return CatalogSearcher(backend)


def _insert_records(backend, records):
    for r in records:
        backend.upsert_asset(r)


class TestGet:
    def test_by_id(self, searcher, backend):
        record = _make_record()
        backend.upsert_asset(record)
        result = searcher.get("abc123def456")
        assert result is not None
        assert result.id == "abc123def456"
        assert result.mime_type == "text/plain"

    def test_by_id_not_found(self, searcher):
        assert searcher.get("nonexistent") is None

    def test_get_by_storage_name(self, searcher, backend):
        record = _make_record()
        backend.upsert_asset(record)
        result = searcher.get_by_storage_name("abc123def456.txt")
        assert result is not None
        assert result.id == "abc123def456"


class TestSearch:
    def test_returns_all(self, searcher, backend):
        records = [_make_record(id=f"r{i}", storage_name=f"r{i}.txt") for i in range(3)]
        _insert_records(backend, records)
        result = searcher.search(SearchQuery())
        assert result.total == 3
        assert len(result.items) == 3

    def test_by_mime_type(self, searcher, backend):
        records = [
            _make_record(id="r1", storage_name="r1.txt", mime_type="text/plain"),
            _make_record(id="r2", storage_name="r2.jpg", mime_type="image/jpeg"),
        ]
        _insert_records(backend, records)
        result = searcher.search(SearchQuery(mime_type="image/jpeg"))
        assert result.total == 1
        assert result.items[0].id == "r2"


class TestCount:
    def test_count(self, searcher, backend):
        records = [_make_record(id=f"c{i}", storage_name=f"c{i}.txt") for i in range(4)]
        _insert_records(backend, records)
        assert searcher.count() == 4


class TestPagination:
    def test_search_pagination(self, searcher, backend):
        records = [_make_record(id=f"p{i}", storage_name=f"p{i}.txt") for i in range(5)]
        _insert_records(backend, records)
        result = searcher.search(SearchQuery(limit=2, offset=0))
        assert result.total == 5
        assert len(result.items) == 2

        result2 = searcher.search(SearchQuery(limit=2, offset=2))
        assert result2.total == 5
        assert len(result2.items) == 2
