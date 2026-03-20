"""Vault inline database surface — text content storage (§5.4.4)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from metadexer.exceptions import VaultIOError, VaultObjectNotFoundError

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Iterator

__all__ = ["VaultInlineStore"]

logger = logging.getLogger(__name__)

_SQLITE_SCHEMA = """\
CREATE TABLE IF NOT EXISTS vault_inline (
    storage_name    TEXT    NOT NULL PRIMARY KEY,
    content         TEXT    NOT NULL,
    stored_at       TEXT    NOT NULL
);
"""

_POSTGRES_SCHEMA = """\
CREATE TABLE IF NOT EXISTS vault_inline (
    storage_name    TEXT        NOT NULL,
    content         TEXT        NOT NULL,
    stored_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_vault_inline PRIMARY KEY (storage_name)
);
"""


class VaultInlineStore:
    """Vault inline text storage. Manages the vault_inline table.

    This class stores small text-based content in a database table
    co-located with the catalog database. The vault module owns this
    table; the catalog module does not read from or write to it.
    """

    def __init__(self, connection: object, dialect: str) -> None:
        self._connection = connection
        self._dialect = dialect  # "sqlite" or "postgres"

    @classmethod
    def from_sqlite(cls, connection: sqlite3.Connection) -> VaultInlineStore:
        """Create an inline store backed by a SQLite connection."""
        return cls(connection=connection, dialect="sqlite")

    @classmethod
    def from_postgres(cls, connection: object) -> VaultInlineStore:
        """Create an inline store backed by a PostgreSQL connection."""
        return cls(connection=connection, dialect="postgres")

    def initialize_schema(self) -> None:
        """Create the vault_inline table if it does not exist. Idempotent."""
        try:
            if self._dialect == "sqlite":
                conn: sqlite3.Connection = self._connection  # type: ignore[assignment]
                conn.execute(_SQLITE_SCHEMA)
                conn.commit()
            else:
                self._connection.execute(_POSTGRES_SCHEMA)  # type: ignore[union-attr]
                self._connection.commit()  # type: ignore[union-attr]
        except Exception as exc:
            raise VaultIOError(f"Failed to initialize vault_inline schema: {exc}") from exc

    def put(self, storage_name: str, content: str) -> bool:
        """Store text content under storage_name.

        Returns True if new, False if storage_name already exists (no-op).
        """
        try:
            if self._dialect == "sqlite":
                conn: sqlite3.Connection = self._connection  # type: ignore[assignment]
                now = datetime.now(UTC).isoformat()
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO vault_inline (storage_name, content, stored_at) "
                    "VALUES (?, ?, ?)",
                    (storage_name, content, now),
                )
                conn.commit()
                return cursor.rowcount == 1
            else:
                now = datetime.now(UTC).isoformat()
                cursor = self._connection.execute(  # type: ignore[union-attr]
                    "INSERT INTO vault_inline (storage_name, content, stored_at) "
                    "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                    (storage_name, content, now),
                )
                self._connection.commit()  # type: ignore[union-attr]
                return cursor.rowcount == 1
        except Exception as exc:
            raise VaultIOError(f"Failed to put inline content {storage_name!r}: {exc}") from exc

    def get(self, storage_name: str) -> str:
        """Retrieve text content by storage_name.

        Raises VaultObjectNotFoundError if the key does not exist.
        """
        try:
            if self._dialect == "sqlite":
                conn: sqlite3.Connection = self._connection  # type: ignore[assignment]
                cursor = conn.execute(
                    "SELECT content FROM vault_inline WHERE storage_name = ?",
                    (storage_name,),
                )
            else:
                cursor = self._connection.execute(  # type: ignore[union-attr]
                    "SELECT content FROM vault_inline WHERE storage_name = %s",
                    (storage_name,),
                )
            row = cursor.fetchone()
        except Exception as exc:
            raise VaultIOError(f"Failed to get inline content {storage_name!r}: {exc}") from exc
        if row is None:
            raise VaultObjectNotFoundError(f"Inline object not found: {storage_name!r}")
        return row[0]

    def head(self, storage_name: str) -> bool:
        """Return True if storage_name exists in the inline store."""
        try:
            if self._dialect == "sqlite":
                conn: sqlite3.Connection = self._connection  # type: ignore[assignment]
                cursor = conn.execute(
                    "SELECT 1 FROM vault_inline WHERE storage_name = ?",
                    (storage_name,),
                )
            else:
                cursor = self._connection.execute(  # type: ignore[union-attr]
                    "SELECT 1 FROM vault_inline WHERE storage_name = %s",
                    (storage_name,),
                )
            return cursor.fetchone() is not None
        except Exception as exc:
            raise VaultIOError(f"Failed to check inline content {storage_name!r}: {exc}") from exc

    def iter_storage_names(self) -> Iterator[str]:
        """Yield every storage_name in the vault_inline table."""
        try:
            if self._dialect == "sqlite":
                conn: sqlite3.Connection = self._connection  # type: ignore[assignment]
                cursor = conn.execute("SELECT storage_name FROM vault_inline ORDER BY storage_name")
            else:
                cursor = self._connection.execute(  # type: ignore[union-attr]
                    "SELECT storage_name FROM vault_inline ORDER BY storage_name"
                )
            for row in cursor:
                yield row[0]
        except Exception as exc:
            raise VaultIOError(f"Failed to iterate inline storage names: {exc}") from exc

    def delete(self, storage_name: str) -> None:
        """Remove the entry identified by storage_name.

        Raises VaultObjectNotFoundError if the key does not exist.
        """
        try:
            if self._dialect == "sqlite":
                conn: sqlite3.Connection = self._connection  # type: ignore[assignment]
                cursor = conn.execute(
                    "DELETE FROM vault_inline WHERE storage_name = ?",
                    (storage_name,),
                )
                conn.commit()
                affected = cursor.rowcount
            else:
                cursor = self._connection.execute(  # type: ignore[union-attr]
                    "DELETE FROM vault_inline WHERE storage_name = %s",
                    (storage_name,),
                )
                self._connection.commit()  # type: ignore[union-attr]
                affected = cursor.rowcount
        except Exception as exc:
            raise VaultIOError(f"Failed to delete inline content {storage_name!r}: {exc}") from exc
        if affected == 0:
            raise VaultObjectNotFoundError(f"Inline object not found: {storage_name!r}")
