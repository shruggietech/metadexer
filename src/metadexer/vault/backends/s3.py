"""S3-compatible vault backend (§5.3)."""

from __future__ import annotations

import io
import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, BinaryIO

import boto3
from botocore.exceptions import ClientError

from metadexer.exceptions import VaultIOError, VaultObjectNotFoundError
from metadexer.vault.backends import VaultBackend

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["S3VaultBackend"]

logger = logging.getLogger(__name__)

# S3 multipart upload threshold (5 MB is the AWS minimum part size).
_MULTIPART_THRESHOLD = 8_388_608


class S3VaultBackend(VaultBackend):
    """S3-compatible vault backend using storage_name as object key."""

    def __init__(
        self,
        endpoint_url: str,
        bucket: str,
        prefix: str = "",
        region: str = "",
        chunk_size: int = 8_388_608,
    ) -> None:
        self._bucket = bucket
        self._prefix = prefix.rstrip("/") + "/" if prefix else ""
        self._chunk_size = chunk_size
        kwargs: dict = {}
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        if region:
            kwargs["region_name"] = region
        self._s3 = boto3.client("s3", **kwargs)

    def _validate_storage_name(self, storage_name: str) -> None:
        """Validate storage_name per §20.1."""
        if not storage_name or len(storage_name) < 2:
            raise VaultIOError(
                f"Invalid storage_name: must be at least 2 characters, got {storage_name!r}"
            )
        if "/" in storage_name or "\\" in storage_name:
            raise VaultIOError(
                f"Invalid storage_name: must not contain path separators, got {storage_name!r}"
            )

    def _key(self, storage_name: str) -> str:
        """Return the full S3 object key for a given storage_name."""
        return f"{self._prefix}{storage_name}"

    def put(self, storage_name: str, source: Path) -> None:
        """Write bytes from source file into the S3 backend under storage_name."""
        self._validate_storage_name(storage_name)
        key = self._key(storage_name)
        try:
            file_size = source.stat().st_size
            if file_size > _MULTIPART_THRESHOLD:
                config = boto3.s3.transfer.TransferConfig(
                    multipart_threshold=_MULTIPART_THRESHOLD,
                    multipart_chunksize=self._chunk_size,
                )
                self._s3.upload_file(str(source), self._bucket, key, Config=config)
            else:
                with open(source, "rb") as f:
                    self._s3.put_object(Bucket=self._bucket, Key=key, Body=f.read())
        except ClientError as exc:
            raise VaultIOError(f"Failed to put object {storage_name!r}: {exc}") from exc
        except OSError as exc:
            raise VaultIOError(f"Failed to read source file for {storage_name!r}: {exc}") from exc

    def get(self, storage_name: str, destination: Path) -> None:
        """Copy stored bytes for storage_name to the destination path."""
        self._validate_storage_name(storage_name)
        key = self._key(storage_name)
        try:
            response = self._s3.get_object(Bucket=self._bucket, Key=key)
            body = response["Body"]
            with open(destination, "wb") as dst:
                while True:
                    chunk = body.read(self._chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
        except ClientError as exc:
            if exc.response["Error"]["Code"] in ("NoSuchKey", "404"):
                raise VaultObjectNotFoundError(f"Object not found: {storage_name!r}") from exc
            raise VaultIOError(f"Failed to get object {storage_name!r}: {exc}") from exc
        except OSError as exc:
            raise VaultIOError(f"Failed to write destination for {storage_name!r}: {exc}") from exc

    def head(self, storage_name: str) -> bool:
        """Return True if storage_name exists in this backend, False otherwise."""
        self._validate_storage_name(storage_name)
        key = self._key(storage_name)
        try:
            self._s3.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] in ("404", "NoSuchKey"):
                return False
            raise VaultIOError(f"Failed to check object {storage_name!r}: {exc}") from exc

    def delete(self, storage_name: str) -> None:
        """Remove the object identified by storage_name."""
        self._validate_storage_name(storage_name)
        if not self.head(storage_name):
            raise VaultObjectNotFoundError(f"Object not found: {storage_name!r}")
        key = self._key(storage_name)
        try:
            self._s3.delete_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            raise VaultIOError(f"Failed to delete object {storage_name!r}: {exc}") from exc

    @contextmanager
    def open_read(self, storage_name: str) -> Iterator[BinaryIO]:
        """Return a context manager that yields a binary readable stream."""
        self._validate_storage_name(storage_name)
        key = self._key(storage_name)
        try:
            response = self._s3.get_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            if exc.response["Error"]["Code"] in ("NoSuchKey", "404"):
                raise VaultObjectNotFoundError(f"Object not found: {storage_name!r}") from exc
            raise VaultIOError(f"Failed to open object {storage_name!r}: {exc}") from exc
        body = response["Body"]
        # Wrap in a BytesIO to ensure standard stream interface
        data = body.read()
        body.close()
        buf = io.BytesIO(data)
        try:
            yield buf  # type: ignore[misc]
        finally:
            buf.close()

    def iter_storage_names(self) -> Iterator[str]:
        """Yield every storage_name present in this backend, sorted."""
        names: list[str] = []
        try:
            paginator = self._s3.get_paginator("list_objects_v2")
            page_kwargs: dict = {"Bucket": self._bucket}
            if self._prefix:
                page_kwargs["Prefix"] = self._prefix
            for page in paginator.paginate(**page_kwargs):
                for obj in page.get("Contents", []):
                    key: str = obj["Key"]
                    if self._prefix and key.startswith(self._prefix):
                        names.append(key[len(self._prefix) :])
                    else:
                        names.append(key)
        except ClientError as exc:
            raise VaultIOError(f"Failed to iterate vault contents: {exc}") from exc
        yield from sorted(names)
