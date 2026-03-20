"""Integration tests for PostgresCatalogBackend (§6.4.1 and §6.8.1)."""

from datetime import UTC, datetime

import psycopg
import pytest

from metadexer.catalog import AssetRecord, SearchQuery
from metadexer.catalog.backends.postgres import PostgresCatalogBackend

pytestmark = pytest.mark.postgres


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


class TestInitializeSchema:
    def test_idempotent(self, pg_backend):
        # Second call should not raise
        pg_backend.initialize_schema()


class TestUpsertAsset:
    def test_new_returns_true(self, pg_backend):
        record = _make_record()
        assert pg_backend.upsert_asset(record) is True

    def test_duplicate_returns_false(self, pg_backend):
        record = _make_record()
        pg_backend.upsert_asset(record)
        assert pg_backend.upsert_asset(record) is False

    def test_preserves_original_on_duplicate(self, pg_backend):
        record1 = _make_record(name_text="original.txt")
        record2 = _make_record(name_text="modified.txt")
        pg_backend.upsert_asset(record1)
        pg_backend.upsert_asset(record2)
        retrieved = pg_backend.get_by_id("abc123def456")
        assert retrieved.name_text == "original.txt"


class TestGetById:
    def test_found(self, pg_backend):
        record = _make_record()
        pg_backend.upsert_asset(record)
        result = pg_backend.get_by_id("abc123def456")
        assert result is not None
        assert result.id == "abc123def456"
        assert result.mime_type == "text/plain"
        assert result.raw_entry == {"id": "abc123def456", "schema_version": 2}

    def test_not_found(self, pg_backend):
        assert pg_backend.get_by_id("nonexistent") is None


class TestGetByStorageName:
    def test_found(self, pg_backend):
        record = _make_record()
        pg_backend.upsert_asset(record)
        result = pg_backend.get_by_storage_name("abc123def456.txt")
        assert result is not None
        assert result.id == "abc123def456"

    def test_not_found(self, pg_backend):
        assert pg_backend.get_by_storage_name("nonexistent") is None


class TestSearch:
    def _insert_sample_records(self, pg_backend):
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
            pg_backend.upsert_asset(r)
        return records

    def test_by_mime_type(self, pg_backend):
        self._insert_sample_records(pg_backend)
        result = pg_backend.search(SearchQuery(mime_type="image/jpeg"))
        assert result.total == 1
        assert result.items[0].id == "r2"

    def test_by_extension(self, pg_backend):
        self._insert_sample_records(pg_backend)
        result = pg_backend.search(SearchQuery(extension="txt"))
        assert result.total == 1
        assert result.items[0].id == "r1"

    def test_by_size_range(self, pg_backend):
        self._insert_sample_records(pg_backend)
        result = pg_backend.search(SearchQuery(size_min=200, size_max=60000))
        assert result.total == 2
        ids = {r.id for r in result.items}
        assert ids == {"r2", "r3"}

    def test_by_modified_date_range(self, pg_backend):
        self._insert_sample_records(pg_backend)
        result = pg_backend.search(
            SearchQuery(
                modified_after=datetime(2026, 1, 15, tzinfo=UTC),
                modified_before=datetime(2026, 2, 15, tzinfo=UTC),
            )
        )
        assert result.total == 1
        assert result.items[0].id == "r1"

    def test_by_name_contains(self, pg_backend):
        self._insert_sample_records(pg_backend)
        result = pg_backend.search(SearchQuery(name_contains="note"))
        assert result.total == 1
        assert result.items[0].id == "r3"

    def test_text_query(self, pg_backend):
        record = _make_record(
            id="fts1",
            storage_name="fts1.txt",
            name_text="document.txt",
            name_normalized="document.txt",
            storage_mode="inline",
        )
        pg_backend.upsert_asset(record, search_text="hello world example text")
        result = pg_backend.search(SearchQuery(text_query="hello"))
        assert result.total == 1
        assert result.items[0].id == "fts1"

    def test_text_query_no_match(self, pg_backend):
        record = _make_record(
            id="fts2",
            storage_name="fts2.txt",
            name_text="other.txt",
            name_normalized="other.txt",
        )
        pg_backend.upsert_asset(record, search_text="alpha beta gamma")
        result = pg_backend.search(SearchQuery(text_query="nonexistent"))
        assert result.total == 0
        assert len(result.items) == 0

    def test_pagination(self, pg_backend):
        for i in range(5):
            r = _make_record(
                id=f"page{i}",
                storage_name=f"page{i}.txt",
                name_text=f"file{i}.txt",
                name_normalized=f"file{i}.txt",
            )
            pg_backend.upsert_asset(r)
        result = pg_backend.search(SearchQuery(limit=2, offset=0))
        assert result.total == 5
        assert len(result.items) == 2

        result2 = pg_backend.search(SearchQuery(limit=2, offset=2))
        assert result2.total == 5
        assert len(result2.items) == 2

    def test_empty_result(self, pg_backend):
        result = pg_backend.search(SearchQuery(mime_type="video/mp4"))
        assert result.total == 0
        assert len(result.items) == 0


class TestCount:
    def test_count(self, pg_backend):
        for i in range(3):
            r = _make_record(
                id=f"cnt{i}",
                storage_name=f"cnt{i}.txt",
            )
            pg_backend.upsert_asset(r)
        assert pg_backend.count() == 3

    def test_count_empty(self, pg_backend):
        assert pg_backend.count() == 0


class TestIterAllStorageNames:
    def test_yields_all_sorted(self, pg_backend):
        for name in ["beta.txt", "alpha.txt", "gamma.txt"]:
            r = _make_record(id=name, storage_name=name)
            pg_backend.upsert_asset(r)
        names = list(pg_backend.iter_all_storage_names())
        assert names == ["alpha.txt", "beta.txt", "gamma.txt"]


class TestClose:
    def test_idempotent(self, pg_dsn):
        b = PostgresCatalogBackend(pg_dsn)
        b.initialize_schema()
        b.close()
        b.close()


class TestConnectionProperty:
    def test_accessible(self, pg_backend):
        conn = pg_backend.connection
        assert isinstance(conn, psycopg.Connection)
