"""Unit tests for SqliteCatalogBackend (§6.4.1 and §6.8.2)."""

import sqlite3
from datetime import UTC, datetime

import pytest

from metadexer.catalog import AssetRecord, SearchQuery
from metadexer.catalog.backends.sqlite import SqliteCatalogBackend


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


class TestInitializeSchema:
    def test_idempotent(self, tmp_path):
        db_path = tmp_path / "catalog.db"
        b = SqliteCatalogBackend(db_path)
        b.initialize_schema()
        b.initialize_schema()
        b.close()


class TestUpsertAsset:
    def test_new_returns_true(self, backend):
        record = _make_record()
        assert backend.upsert_asset(record) is True

    def test_duplicate_returns_false(self, backend):
        record = _make_record()
        backend.upsert_asset(record)
        assert backend.upsert_asset(record) is False

    def test_preserves_original_on_duplicate(self, backend):
        record1 = _make_record(name_text="original.txt")
        record2 = _make_record(name_text="modified.txt")
        backend.upsert_asset(record1)
        backend.upsert_asset(record2)
        retrieved = backend.get_by_id("abc123def456")
        assert retrieved.name_text == "original.txt"


class TestGetById:
    def test_found(self, backend):
        record = _make_record()
        backend.upsert_asset(record)
        result = backend.get_by_id("abc123def456")
        assert result is not None
        assert result.id == "abc123def456"
        assert result.mime_type == "text/plain"
        assert result.raw_entry == {"id": "abc123def456", "schema_version": 2}

    def test_not_found(self, backend):
        assert backend.get_by_id("nonexistent") is None


class TestGetByStorageName:
    def test_found(self, backend):
        record = _make_record()
        backend.upsert_asset(record)
        result = backend.get_by_storage_name("abc123def456.txt")
        assert result is not None
        assert result.id == "abc123def456"

    def test_not_found(self, backend):
        assert backend.get_by_storage_name("nonexistent") is None


class TestSearch:
    def _insert_sample_records(self, backend):
        records = [
            _make_record(
                id="r1",
                storage_name="r1.txt",
                mime_type="text/plain",
                extension="txt",
                size_bytes=100,
                name_text="readme.txt",
                name_normalized="readme.txt",
                ts_modified=datetime(2026, 2, 1, tzinfo=UTC),
            ),
            _make_record(
                id="r2",
                storage_name="r2.jpg",
                mime_type="image/jpeg",
                extension="jpg",
                size_bytes=50000,
                name_text="photo.jpg",
                name_normalized="photo.jpg",
                ts_modified=datetime(2026, 1, 10, tzinfo=UTC),
            ),
            _make_record(
                id="r3",
                storage_name="r3.txt",
                mime_type="text/markdown",
                extension="md",
                size_bytes=500,
                name_text="notes.md",
                name_normalized="notes.md",
                ts_modified=datetime(2026, 3, 1, tzinfo=UTC),
            ),
        ]
        for r in records:
            backend.upsert_asset(r)
        return records

    def test_by_mime_type(self, backend):
        self._insert_sample_records(backend)
        result = backend.search(SearchQuery(mime_type="image/jpeg"))
        assert result.total == 1
        assert result.items[0].id == "r2"

    def test_by_extension(self, backend):
        self._insert_sample_records(backend)
        result = backend.search(SearchQuery(extension="txt"))
        assert result.total == 1
        assert result.items[0].id == "r1"

    def test_by_size_range(self, backend):
        self._insert_sample_records(backend)
        result = backend.search(SearchQuery(size_min=200, size_max=60000))
        assert result.total == 2
        ids = {r.id for r in result.items}
        assert ids == {"r2", "r3"}

    def test_by_modified_date_range(self, backend):
        self._insert_sample_records(backend)
        result = backend.search(
            SearchQuery(
                modified_after=datetime(2026, 1, 15, tzinfo=UTC),
                modified_before=datetime(2026, 2, 15, tzinfo=UTC),
            )
        )
        assert result.total == 1
        assert result.items[0].id == "r1"

    def test_by_name_contains(self, backend):
        self._insert_sample_records(backend)
        result = backend.search(SearchQuery(name_contains="note"))
        assert result.total == 1
        assert result.items[0].id == "r3"

    def test_text_query_fts5(self, backend):
        record = _make_record(
            id="fts1",
            storage_name="fts1.txt",
            name_text="document.txt",
            name_normalized="document.txt",
            storage_mode="inline",
        )
        backend.upsert_asset(record, search_text="hello world example text")
        result = backend.search(SearchQuery(text_query="hello"))
        assert result.total == 1
        assert result.items[0].id == "fts1"

    def test_text_query_no_match(self, backend):
        record = _make_record(
            id="fts2",
            storage_name="fts2.txt",
            name_text="other.txt",
            name_normalized="other.txt",
        )
        backend.upsert_asset(record, search_text="alpha beta gamma")
        result = backend.search(SearchQuery(text_query="nonexistent"))
        assert result.total == 0
        assert len(result.items) == 0

    def test_pagination(self, backend):
        for i in range(5):
            r = _make_record(
                id=f"page{i}",
                storage_name=f"page{i}.txt",
                name_text=f"file{i}.txt",
                name_normalized=f"file{i}.txt",
            )
            backend.upsert_asset(r)
        result = backend.search(SearchQuery(limit=2, offset=0))
        assert result.total == 5
        assert len(result.items) == 2

        result2 = backend.search(SearchQuery(limit=2, offset=2))
        assert result2.total == 5
        assert len(result2.items) == 2

    def test_empty_result(self, backend):
        result = backend.search(SearchQuery(mime_type="video/mp4"))
        assert result.total == 0
        assert len(result.items) == 0


class TestCount:
    def test_count(self, backend):
        for i in range(3):
            r = _make_record(
                id=f"cnt{i}",
                storage_name=f"cnt{i}.txt",
            )
            backend.upsert_asset(r)
        assert backend.count() == 3

    def test_count_empty(self, backend):
        assert backend.count() == 0


class TestIterAllStorageNames:
    def test_yields_all_sorted(self, backend):
        for name in ["beta.txt", "alpha.txt", "gamma.txt"]:
            r = _make_record(id=name, storage_name=name)
            backend.upsert_asset(r)
        names = list(backend.iter_all_storage_names())
        assert names == ["alpha.txt", "beta.txt", "gamma.txt"]


class TestClose:
    def test_idempotent(self, tmp_path):
        db_path = tmp_path / "catalog.db"
        b = SqliteCatalogBackend(db_path)
        b.initialize_schema()
        b.close()
        b.close()


class TestConnectionProperty:
    def test_accessible(self, backend):
        conn = backend.connection
        assert isinstance(conn, sqlite3.Connection)
