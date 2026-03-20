"""Unit tests for VaultInlineStore (§5.4.4)."""

import sqlite3

import pytest

from metadexer.exceptions import VaultObjectNotFoundError
from metadexer.vault.inline import VaultInlineStore


@pytest.fixture()
def inline_store():
    """Create a VaultInlineStore backed by an in-memory SQLite database."""
    conn = sqlite3.connect(":memory:")
    store = VaultInlineStore.from_sqlite(conn)
    store.initialize_schema()
    return store


class TestInitializeSchema:
    def test_idempotent(self):
        conn = sqlite3.connect(":memory:")
        store = VaultInlineStore.from_sqlite(conn)
        store.initialize_schema()
        store.initialize_schema()  # should not raise


class TestPut:
    def test_new_returns_true(self, inline_store):
        assert inline_store.put("ab123456.txt", "hello world") is True

    def test_duplicate_returns_false(self, inline_store):
        inline_store.put("ab123456.txt", "hello world")
        assert inline_store.put("ab123456.txt", "hello world") is False


class TestGet:
    def test_retrieves_correct_content(self, inline_store):
        inline_store.put("ab123456.txt", "hello world")
        assert inline_store.get("ab123456.txt") == "hello world"

    def test_not_found(self, inline_store):
        with pytest.raises(VaultObjectNotFoundError):
            inline_store.get("zz000000.txt")


class TestHead:
    def test_existing(self, inline_store):
        inline_store.put("ab123456.txt", "content")
        assert inline_store.head("ab123456.txt") is True

    def test_missing(self, inline_store):
        assert inline_store.head("zz000000.txt") is False


class TestDelete:
    def test_removes_entry(self, inline_store):
        inline_store.put("ab123456.txt", "content")
        inline_store.delete("ab123456.txt")
        assert inline_store.head("ab123456.txt") is False

    def test_not_found(self, inline_store):
        with pytest.raises(VaultObjectNotFoundError):
            inline_store.delete("zz000000.txt")


class TestIterStorageNames:
    def test_yields_all_sorted(self, inline_store):
        inline_store.put("cc111111.txt", "c")
        inline_store.put("aa222222.txt", "a")
        inline_store.put("bb333333.txt", "b")
        result = list(inline_store.iter_storage_names())
        assert result == ["aa222222.txt", "bb333333.txt", "cc111111.txt"]

    def test_empty(self, inline_store):
        assert list(inline_store.iter_storage_names()) == []


class TestUnicodeContent:
    def test_preserves_unicode(self, inline_store):
        content = "日本語テスト 🎉 résumé"
        inline_store.put("ab123456.txt", content)
        assert inline_store.get("ab123456.txt") == content
