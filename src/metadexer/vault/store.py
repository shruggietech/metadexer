"""Vault storage operations: put, get, head, verify, prune (§5.4.2, §5.4.3)."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from metadexer.exceptions import VaultError, VaultObjectNotFoundError

if TYPE_CHECKING:
    from pathlib import Path

    from metadexer.vault.backends import VaultBackend
    from metadexer.vault.inline import VaultInlineStore

__all__ = ["PruneResult", "VaultStore", "VerifyResult"]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VerifyResult:
    """Result of a single-object vault verification."""

    storage_name: str
    passed: bool
    checked: dict[str, bool]
    expected: dict[str, str]
    actual: dict[str, str]


@dataclass(frozen=True)
class PruneResult:
    """Result of a vault prune operation."""

    deleted: int
    failed: int
    dry_run: bool
    storage_names: tuple[str, ...]


class VaultStore:
    """Vault module public API. Wraps a VaultBackend and optional VaultInlineStore."""

    def __init__(
        self,
        backend: VaultBackend,
        chunk_size: int = 8_388_608,
        inline_store: VaultInlineStore | None = None,
    ) -> None:
        """Initialize with a configured backend, chunk size, and optional inline store."""
        self._backend = backend
        self._chunk_size = chunk_size
        self._inline_store = inline_store

    def put(self, storage_name: str, source: Path) -> bool:
        """Store bytes from source under storage_name (§5.2.1, put).

        Returns True if bytes were written (new object), False if the object
        already existed (deduplicated).
        """
        if self._backend.head(storage_name):
            return False
        self._backend.put(storage_name, source)
        return True

    def get(self, storage_name: str, destination: Path) -> None:
        """Retrieve bytes to destination (§5.2.1, get)."""
        self._backend.get(storage_name, destination)

    def head(self, storage_name: str) -> bool:
        """Check existence without retrieving bytes (§5.2.1, head)."""
        return self._backend.head(storage_name)

    def put_inline(self, storage_name: str, content: str) -> bool:
        """Store text content under storage_name (§5.2.2, put_inline).

        Raises VaultError if no inline_store was provided at construction.
        """
        if self._inline_store is None:
            raise VaultError("No inline store configured")
        return self._inline_store.put(storage_name, content)

    def get_inline(self, storage_name: str) -> str:
        """Retrieve text content by storage_name (§5.2.2, get_inline).

        Raises VaultError if no inline_store was provided at construction.
        """
        if self._inline_store is None:
            raise VaultError("No inline store configured")
        return self._inline_store.get(storage_name)

    def verify(
        self,
        storage_name: str,
        expected_hashes: dict[str, str],
    ) -> VerifyResult:
        """Re-hash stored bytes and compare against expected hashes (§5.2.1, verify)."""
        hashers = {}
        for algo in expected_hashes:
            hashers[algo] = hashlib.new(algo)

        with self._backend.open_read(storage_name) as f:
            while True:
                chunk = f.read(self._chunk_size)
                if not chunk:
                    break
                for h in hashers.values():
                    h.update(chunk)

        actual: dict[str, str] = {}
        checked: dict[str, bool] = {}
        for algo, hasher in hashers.items():
            computed = hasher.hexdigest().upper()
            actual[algo] = computed
            checked[algo] = computed == expected_hashes[algo].upper()

        return VerifyResult(
            storage_name=storage_name,
            passed=all(checked.values()),
            checked=checked,
            expected=expected_hashes,
            actual=actual,
        )

    def prune(
        self,
        unreferenced: set[str],
        *,
        dry_run: bool = True,
    ) -> PruneResult:
        """Remove unreferenced objects from the vault (§5.2.1, prune)."""
        names = tuple(sorted(unreferenced))
        if dry_run:
            return PruneResult(
                deleted=0,
                failed=0,
                dry_run=True,
                storage_names=names,
            )

        deleted = 0
        failed = 0
        for name in names:
            try:
                self._backend.delete(name)
                deleted += 1
            except (VaultObjectNotFoundError, VaultError):
                logger.warning("Failed to prune object %r", name)
                failed += 1

        return PruneResult(
            deleted=deleted,
            failed=failed,
            dry_run=False,
            storage_names=names,
        )
