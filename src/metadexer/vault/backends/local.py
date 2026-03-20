"""Local filesystem vault backend (§5.3)."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import IO, TYPE_CHECKING, BinaryIO

from metadexer.exceptions import VaultIOError, VaultObjectNotFoundError
from metadexer.vault.backends import VaultBackend

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["LocalVaultBackend"]

logger = logging.getLogger(__name__)


class LocalVaultBackend(VaultBackend):
    """Local filesystem vault backend using two-character prefix sharding."""

    def __init__(self, root: Path, chunk_size: int = 8_388_608) -> None:
        self._root = root.resolve()
        self._chunk_size = chunk_size
        self._root.mkdir(parents=True, exist_ok=True)

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

    def _object_path(self, storage_name: str) -> Path:
        """Return the sharded storage path for a given storage_name."""
        return self._root / storage_name[:2].lower() / storage_name

    def put(self, storage_name: str, source: Path) -> None:
        """Write bytes from source file into the backend under storage_name."""
        self._validate_storage_name(storage_name)
        obj_path = self._object_path(storage_name)
        try:
            obj_path.parent.mkdir(parents=True, exist_ok=True)
            with open(source, "rb") as src, open(obj_path, "wb") as dst:
                while True:
                    chunk = src.read(self._chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
        except OSError as exc:
            raise VaultIOError(f"Failed to put object {storage_name!r}: {exc}") from exc

    def get(self, storage_name: str, destination: Path) -> None:
        """Copy stored bytes for storage_name to the destination path."""
        self._validate_storage_name(storage_name)
        obj_path = self._object_path(storage_name)
        if not obj_path.exists():
            raise VaultObjectNotFoundError(f"Object not found: {storage_name!r}")
        try:
            with open(obj_path, "rb") as src, open(destination, "wb") as dst:
                while True:
                    chunk = src.read(self._chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
        except OSError as exc:
            raise VaultIOError(f"Failed to get object {storage_name!r}: {exc}") from exc

    def head(self, storage_name: str) -> bool:
        """Return True if storage_name exists in this backend, False otherwise."""
        self._validate_storage_name(storage_name)
        return self._object_path(storage_name).exists()

    def delete(self, storage_name: str) -> None:
        """Remove the object identified by storage_name."""
        self._validate_storage_name(storage_name)
        obj_path = self._object_path(storage_name)
        if not obj_path.exists():
            raise VaultObjectNotFoundError(f"Object not found: {storage_name!r}")
        try:
            obj_path.unlink()
        except OSError as exc:
            raise VaultIOError(f"Failed to delete object {storage_name!r}: {exc}") from exc

    @contextmanager
    def open_read(self, storage_name: str) -> Iterator[BinaryIO]:
        """Return a context manager that yields a binary readable stream."""
        self._validate_storage_name(storage_name)
        obj_path = self._object_path(storage_name)
        if not obj_path.exists():
            raise VaultObjectNotFoundError(f"Object not found: {storage_name!r}")
        try:
            f: IO[bytes] = open(obj_path, "rb")  # noqa: SIM115
        except OSError as exc:
            raise VaultIOError(f"Failed to open object {storage_name!r}: {exc}") from exc
        try:
            yield f  # type: ignore[misc]
        finally:
            f.close()

    def iter_storage_names(self) -> Iterator[str]:
        """Yield every storage_name present in this backend, sorted."""
        names: list[str] = []
        try:
            for prefix_dir in sorted(self._root.iterdir()):
                if prefix_dir.is_dir():
                    for obj_file in sorted(prefix_dir.iterdir()):
                        if obj_file.is_file():
                            names.append(obj_file.name)
        except OSError as exc:
            raise VaultIOError(f"Failed to iterate vault contents: {exc}") from exc
        yield from names
