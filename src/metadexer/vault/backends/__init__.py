"""Vault storage backend implementations."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import AbstractContextManager
from pathlib import Path
from typing import BinaryIO

__all__ = ["VaultBackend"]


class VaultBackend(ABC):
    """Abstract interface for vault storage backends."""

    @abstractmethod
    def put(self, storage_name: str, source: Path) -> None:
        """Write bytes from source file into the backend under storage_name.

        The caller (VaultStore) guarantees that storage_name does not already
        exist in this backend before calling put. Implementations MUST NOT
        perform their own existence checks. Implementations MUST validate
        that storage_name conforms to the expected key pattern (§20.1)
        before performing any I/O.
        """

    @abstractmethod
    def get(self, storage_name: str, destination: Path) -> None:
        """Copy stored bytes for storage_name to the destination path.

        Raises VaultObjectNotFoundError if storage_name does not exist.
        Implementations MUST use chunked I/O (§20.4). The chunk size is
        provided to the backend at construction time.
        """

    @abstractmethod
    def head(self, storage_name: str) -> bool:
        """Return True if storage_name exists in this backend, False otherwise."""

    @abstractmethod
    def delete(self, storage_name: str) -> None:
        """Remove the object identified by storage_name.

        Raises VaultObjectNotFoundError if storage_name does not exist.
        This method is called by VaultStore.prune for each unreferenced
        object. Backends MUST NOT perform cascade deletions or remove
        anything other than the single named object.
        """

    @abstractmethod
    def open_read(self, storage_name: str) -> AbstractContextManager[BinaryIO]:
        """Return a context manager that yields a binary readable stream.

        Usage:
            with backend.open_read("a1b2c3d4.mp4") as f:
                chunk = f.read(chunk_size)

        Used by VaultStore.verify to stream bytes through hash computation
        without writing to an intermediate file. Raises VaultObjectNotFoundError
        if storage_name does not exist.
        """

    @abstractmethod
    def iter_storage_names(self) -> Iterator[str]:
        """Yield every storage_name present in this backend.

        Used by catalog reconciliation to compare vault contents against
        catalog records. Implementations SHOULD yield names in a stable
        order (lexicographic) but callers MUST NOT depend on ordering.
        """
