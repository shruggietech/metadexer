"""Unit tests for catalog shared types (§6.4.3)."""

import dataclasses
from datetime import UTC, datetime

import pytest

from metadexer.catalog import AssetRecord, IngestResult, SearchQuery, SearchResult


def _make_record(**overrides):
    defaults = {
        "id": "abc123",
        "schema_version": 2,
        "type": "file",
        "mime_type": "text/plain",
        "extension": "txt",
        "name_text": "hello.txt",
        "name_normalized": "hello.txt",
        "size_bytes": 42,
        "ts_modified": datetime(2026, 1, 1, tzinfo=UTC),
        "ts_created": datetime(2026, 1, 1, tzinfo=UTC),
        "storage_name": "abc123.txt",
        "storage_mode": "vault",
        "raw_entry": {"id": "abc123"},
        "ingested_at": datetime(2026, 3, 19, tzinfo=UTC),
    }
    defaults.update(overrides)
    return AssetRecord(**defaults)


class TestAssetRecord:
    def test_instantiation(self):
        record = _make_record()
        assert record.id == "abc123"
        assert record.schema_version == 2
        assert record.type == "file"
        assert record.mime_type == "text/plain"
        assert record.extension == "txt"
        assert record.name_text == "hello.txt"
        assert record.name_normalized == "hello.txt"
        assert record.size_bytes == 42
        assert record.storage_name == "abc123.txt"
        assert record.storage_mode == "vault"
        assert record.raw_entry == {"id": "abc123"}
        assert record.ingested_at == datetime(2026, 3, 19, tzinfo=UTC)

    def test_no_inline_content_field(self):
        field_names = {f.name for f in dataclasses.fields(AssetRecord)}
        assert "inline_content" not in field_names

    def test_frozen(self):
        record = _make_record()
        with pytest.raises(dataclasses.FrozenInstanceError):
            record.id = "changed"


class TestSearchQuery:
    def test_defaults(self):
        q = SearchQuery()
        assert q.text_query is None
        assert q.mime_type is None
        assert q.mime_prefix is None
        assert q.extension is None
        assert q.type is None
        assert q.size_min is None
        assert q.size_max is None
        assert q.modified_after is None
        assert q.modified_before is None
        assert q.name_contains is None
        assert q.limit == 100
        assert q.offset == 0


class TestSearchResult:
    def test_construction(self):
        record = _make_record()
        query = SearchQuery()
        result = SearchResult(items=(record,), total=1, query=query)
        assert result.items == (record,)
        assert result.total == 1
        assert result.query is query


class TestIngestResult:
    def test_construction(self):
        result = IngestResult(new=5, duplicate=2, failed=1, errors=(("idx0", "bad schema"),))
        assert result.new == 5
        assert result.duplicate == 2
        assert result.failed == 1
        assert result.errors == (("idx0", "bad schema"),)
