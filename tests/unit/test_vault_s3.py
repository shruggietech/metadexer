"""Unit tests for S3VaultBackend (§5.3, §5.4.1)."""

import boto3
import pytest
from moto import mock_aws

from metadexer.exceptions import VaultIOError, VaultObjectNotFoundError
from metadexer.vault.backends.s3 import S3VaultBackend

TEST_BUCKET = "test-vault-bucket"
TEST_REGION = "us-east-1"


@pytest.fixture()
def _mock_aws():
    """Activate moto mock for all AWS services."""
    with mock_aws():
        yield


@pytest.fixture()
def s3_client(_mock_aws):
    """Return a boto3 S3 client inside the moto mock."""
    client = boto3.client("s3", region_name=TEST_REGION)
    client.create_bucket(Bucket=TEST_BUCKET)
    return client


@pytest.fixture()
def vault(_mock_aws, s3_client):
    """Create an S3VaultBackend pointed at the moto mock bucket."""
    return S3VaultBackend(
        endpoint_url="",
        bucket=TEST_BUCKET,
        prefix="",
        region=TEST_REGION,
    )


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
    def test_large_file_small_chunks(self, vault, tmp_path, _mock_aws, s3_client):
        small_vault = S3VaultBackend(
            endpoint_url="",
            bucket=TEST_BUCKET,
            prefix="",
            region=TEST_REGION,
            chunk_size=1024,
        )
        src = tmp_path / "large.bin"
        data = b"x" * 8192  # 8 KB, larger than 1024-byte chunk size
        src.write_bytes(data)
        small_vault.put("ab123456.bin", src)
        dest = tmp_path / "large_out.bin"
        small_vault.get("ab123456.bin", dest)
        assert dest.read_bytes() == data


class TestPrefixIsolation:
    def test_key_structure_with_prefix(self, _mock_aws, s3_client, tmp_path):
        """Verify objects are stored under the configured prefix."""
        vault_with_prefix = S3VaultBackend(
            endpoint_url="",
            bucket=TEST_BUCKET,
            prefix="myprefix",
            region=TEST_REGION,
        )
        src = tmp_path / "prefixed.bin"
        src.write_bytes(b"prefix test content")
        vault_with_prefix.put("abcdef123456.dat", src)

        # Verify the object exists under the prefix in S3
        response = s3_client.list_objects_v2(Bucket=TEST_BUCKET, Prefix="myprefix/")
        keys = [obj["Key"] for obj in response.get("Contents", [])]
        assert "myprefix/abcdef123456.dat" in keys

        # Verify iter_storage_names strips the prefix
        names = list(vault_with_prefix.iter_storage_names())
        assert "abcdef123456.dat" in names

        # Verify round-trip through prefixed vault
        dest = tmp_path / "prefixed_out.bin"
        vault_with_prefix.get("abcdef123456.dat", dest)
        assert dest.read_bytes() == b"prefix test content"
