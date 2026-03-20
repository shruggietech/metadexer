"""Unit tests for VaultStore facade (§5.4.2, §5.4.3)."""

import hashlib
import sqlite3

import pytest

from metadexer.exceptions import VaultError, VaultObjectNotFoundError
from metadexer.vault.backends.local import LocalVaultBackend
from metadexer.vault.inline import VaultInlineStore
from metadexer.vault.store import PruneResult, VaultStore, VerifyResult


@pytest.fixture()
def backend(tmp_path):
    """Create a LocalVaultBackend rooted at tmp_path/vault."""
    return LocalVaultBackend(root=tmp_path / "vault")


@pytest.fixture()
def inline_store():
    """Create a VaultInlineStore backed by an in-memory SQLite database."""
    conn = sqlite3.connect(":memory:")
    store = VaultInlineStore.from_sqlite(conn)
    store.initialize_schema()
    return store


@pytest.fixture()
def vault_store(backend, inline_store):
    """Create a VaultStore with both file backend and inline store."""
    return VaultStore(backend=backend, inline_store=inline_store)


@pytest.fixture()
def vault_store_no_inline(backend):
    """Create a VaultStore without an inline store."""
    return VaultStore(backend=backend)


@pytest.fixture()
def sample_file(tmp_path):
    """Write a small sample file and return its path."""
    p = tmp_path / "sample.bin"
    p.write_bytes(b"hello vault content")
    return p


# ── File-based operations ──────────────────────────────────────────────────


class TestPut:
    def test_new_returns_true(self, vault_store, sample_file):
        assert vault_store.put("abcdef123456.dat", sample_file) is True

    def test_duplicate_returns_false(self, vault_store, sample_file):
        vault_store.put("abcdef123456.dat", sample_file)
        assert vault_store.put("abcdef123456.dat", sample_file) is False


class TestGet:
    def test_retrieves_correct_bytes(self, vault_store, sample_file, tmp_path):
        vault_store.put("abcdef123456.dat", sample_file)
        dest = tmp_path / "out.dat"
        vault_store.get("abcdef123456.dat", dest)
        assert dest.read_bytes() == sample_file.read_bytes()


class TestHead:
    def test_delegates(self, vault_store, sample_file):
        assert vault_store.head("abcdef123456.dat") is False
        vault_store.put("abcdef123456.dat", sample_file)
        assert vault_store.head("abcdef123456.dat") is True


class TestVerify:
    def test_passing(self, vault_store, sample_file):
        vault_store.put("abcdef123456.dat", sample_file)
        content = sample_file.read_bytes()
        expected = {
            "md5": hashlib.md5(content).hexdigest().upper(),
            "sha256": hashlib.sha256(content).hexdigest().upper(),
        }
        result = vault_store.verify("abcdef123456.dat", expected)
        assert isinstance(result, VerifyResult)
        assert result.passed is True
        assert result.checked["md5"] is True
        assert result.checked["sha256"] is True

    def test_failing(self, vault_store, sample_file):
        vault_store.put("abcdef123456.dat", sample_file)
        expected = {
            "md5": "0" * 32,
            "sha256": "0" * 64,
        }
        result = vault_store.verify("abcdef123456.dat", expected)
        assert result.passed is False

    def test_not_found(self, vault_store):
        with pytest.raises(VaultObjectNotFoundError):
            vault_store.verify("zz000000.dat", {"md5": "abc"})


class TestPrune:
    def test_dry_run(self, vault_store, sample_file):
        vault_store.put("abcdef123456.dat", sample_file)
        result = vault_store.prune({"abcdef123456.dat"}, dry_run=True)
        assert isinstance(result, PruneResult)
        assert result.dry_run is True
        assert result.deleted == 0
        assert "abcdef123456.dat" in result.storage_names
        # Object still exists after dry run
        assert vault_store.head("abcdef123456.dat") is True

    def test_actual_prune(self, vault_store, sample_file):
        vault_store.put("abcdef123456.dat", sample_file)
        result = vault_store.prune({"abcdef123456.dat"}, dry_run=False)
        assert result.dry_run is False
        assert result.deleted == 1
        assert result.failed == 0
        assert vault_store.head("abcdef123456.dat") is False

    def test_partial_failure(self, vault_store, sample_file):
        vault_store.put("abcdef123456.dat", sample_file)
        result = vault_store.prune({"abcdef123456.dat", "zz000000.dat"}, dry_run=False)
        assert result.deleted == 1
        assert result.failed == 1


# ── Inline operations ──────────────────────────────────────────────────────


class TestPutInline:
    def test_new_returns_true(self, vault_store):
        assert vault_store.put_inline("ab123456.txt", "hello") is True

    def test_duplicate_returns_false(self, vault_store):
        vault_store.put_inline("ab123456.txt", "hello")
        assert vault_store.put_inline("ab123456.txt", "hello") is False


class TestGetInline:
    def test_retrieves_correct_content(self, vault_store):
        vault_store.put_inline("ab123456.txt", "hello world")
        assert vault_store.get_inline("ab123456.txt") == "hello world"


class TestNoInlineStore:
    def test_put_inline_raises(self, vault_store_no_inline):
        with pytest.raises(VaultError, match="No inline store configured"):
            vault_store_no_inline.put_inline("ab123456.txt", "hello")

    def test_get_inline_raises(self, vault_store_no_inline):
        with pytest.raises(VaultError, match="No inline store configured"):
            vault_store_no_inline.get_inline("ab123456.txt")
