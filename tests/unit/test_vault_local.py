"""Unit tests for LocalVaultBackend (§5.3, §5.4.1)."""

import pytest

from metadexer.exceptions import VaultIOError, VaultObjectNotFoundError
from metadexer.vault.backends.local import LocalVaultBackend


@pytest.fixture()
def vault(tmp_path):
    """Create a LocalVaultBackend rooted at tmp_path/vault."""
    return LocalVaultBackend(root=tmp_path / "vault")


@pytest.fixture()
def sample_file(tmp_path):
    """Write a small sample file and return its path."""
    p = tmp_path / "sample.bin"
    p.write_bytes(b"hello vault content")
    return p


class TestPutAndGet:
    def test_round_trip(self, vault, sample_file, tmp_path):
        vault.put("abcdef123456.dat", sample_file)
        dest = tmp_path / "out.dat"
        vault.get("abcdef123456.dat", dest)
        assert dest.read_bytes() == sample_file.read_bytes()


class TestHead:
    def test_existing(self, vault, sample_file):
        vault.put("abcdef123456.dat", sample_file)
        assert vault.head("abcdef123456.dat") is True

    def test_missing(self, vault):
        assert vault.head("zz000000.dat") is False


class TestGetErrors:
    def test_not_found(self, vault, tmp_path):
        with pytest.raises(VaultObjectNotFoundError):
            vault.get("zz000000.dat", tmp_path / "out.dat")


class TestDelete:
    def test_removes_object(self, vault, sample_file):
        vault.put("abcdef123456.dat", sample_file)
        vault.delete("abcdef123456.dat")
        assert vault.head("abcdef123456.dat") is False

    def test_not_found(self, vault):
        with pytest.raises(VaultObjectNotFoundError):
            vault.delete("zz000000.dat")


class TestOpenRead:
    def test_streams_bytes(self, vault, sample_file):
        vault.put("abcdef123456.dat", sample_file)
        with vault.open_read("abcdef123456.dat") as f:
            data = f.read()
        assert data == sample_file.read_bytes()

    def test_not_found(self, vault):
        with pytest.raises(VaultObjectNotFoundError), vault.open_read("zz000000.dat") as f:
            f.read()


class TestIterStorageNames:
    def test_multiple(self, vault, tmp_path):
        names = ["cc111111.dat", "aa222222.dat", "bb333333.dat"]
        for name in names:
            src = tmp_path / name
            src.write_bytes(b"data-" + name.encode())
            vault.put(name, src)
        result = list(vault.iter_storage_names())
        assert result == sorted(names)

    def test_empty(self, vault):
        assert list(vault.iter_storage_names()) == []


class TestPrefixSharding:
    def test_directory_structure(self, vault, sample_file, tmp_path):
        vault.put("abcdef123456.txt", sample_file)
        expected = vault._root / "ab" / "abcdef123456.txt"
        assert expected.exists()


class TestPathValidation:
    def test_slash(self, vault, sample_file):
        with pytest.raises(VaultIOError):
            vault.put("ab/cd.dat", sample_file)

    def test_backslash(self, vault, sample_file):
        with pytest.raises(VaultIOError):
            vault.put("ab\\cd.dat", sample_file)

    def test_empty(self, vault, sample_file):
        with pytest.raises(VaultIOError):
            vault.put("", sample_file)

    def test_single_char(self, vault, sample_file):
        with pytest.raises(VaultIOError):
            vault.put("a", sample_file)


class TestChunkedIO:
    def test_large_file_small_chunks(self, vault, tmp_path):
        small_vault = LocalVaultBackend(root=tmp_path / "chunked_vault", chunk_size=1024)
        src = tmp_path / "large.bin"
        data = b"x" * 8192  # 8 KB, larger than 1024-byte chunk size
        src.write_bytes(data)
        small_vault.put("ab123456.bin", src)
        dest = tmp_path / "large_out.bin"
        small_vault.get("ab123456.bin", dest)
        assert dest.read_bytes() == data
