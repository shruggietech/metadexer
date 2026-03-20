"""SQLite catalog backend (§6.4.1 and §6.8.2)."""

import json
import logging
import sqlite3
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from metadexer.catalog import AssetRecord, SearchQuery, SearchResult
from metadexer.catalog.backends import CatalogBackend
from metadexer.exceptions import CatalogConnectionError, CatalogSchemaError

logger = logging.getLogger(__name__)

__all__ = ["SqliteCatalogBackend"]

_CREATE_ASSETS_TABLE = """\
CREATE TABLE IF NOT EXISTS assets (
    id              TEXT        NOT NULL PRIMARY KEY,
    schema_version  INTEGER     NOT NULL,
    type            TEXT        NOT NULL,
    mime_type       TEXT,
    extension       TEXT,
    name_text       TEXT,
    name_normalized TEXT,
    size_bytes      INTEGER,
    ts_modified     TEXT,
    ts_created      TEXT,
    storage_name    TEXT        NOT NULL UNIQUE,
    storage_mode    TEXT        NOT NULL CHECK (storage_mode IN ('vault', 'inline')),
    raw_entry       TEXT        NOT NULL,
    ingested_at     TEXT        NOT NULL
);
"""

_CREATE_INDEXES = """\
CREATE INDEX IF NOT EXISTS idx_assets_mime_type   ON assets (mime_type);
CREATE INDEX IF NOT EXISTS idx_assets_extension   ON assets (extension);
CREATE INDEX IF NOT EXISTS idx_assets_size_bytes  ON assets (size_bytes);
CREATE INDEX IF NOT EXISTS idx_assets_ts_modified ON assets (ts_modified);
"""

_CREATE_FTS = """\
CREATE VIRTUAL TABLE IF NOT EXISTS assets_fts USING fts5(
    id UNINDEXED,
    name_text,
    search_text
);
"""


def _datetime_to_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()


def _iso_to_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value)


def _row_to_record(row: sqlite3.Row) -> AssetRecord:
    return AssetRecord(
        id=row["id"],
        schema_version=row["schema_version"],
        type=row["type"],
        mime_type=row["mime_type"],
        extension=row["extension"],
        name_text=row["name_text"],
        name_normalized=row["name_normalized"],
        size_bytes=row["size_bytes"],
        ts_modified=_iso_to_datetime(row["ts_modified"]),
        ts_created=_iso_to_datetime(row["ts_created"]),
        storage_name=row["storage_name"],
        storage_mode=row["storage_mode"],
        raw_entry=json.loads(row["raw_entry"]),
        ingested_at=_iso_to_datetime(row["ingested_at"]),
    )


class SqliteCatalogBackend(CatalogBackend):
    """SQLite implementation of the CatalogBackend interface."""

    def __init__(self, path: Path) -> None:
        try:
            self._conn = sqlite3.connect(str(path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.Error as exc:
            raise CatalogConnectionError(f"Failed to open SQLite database at {path}") from exc

    @property
    def connection(self) -> sqlite3.Connection:
        """Expose the underlying connection for VaultInlineStore co-location."""
        return self._conn

    def initialize_schema(self) -> None:
        try:
            self._conn.executescript(_CREATE_ASSETS_TABLE + _CREATE_INDEXES + _CREATE_FTS)
        except sqlite3.Error as exc:
            raise CatalogSchemaError("Failed to initialize SQLite catalog schema") from exc

    def upsert_asset(self, record: AssetRecord, search_text: str | None = None) -> bool:
        cursor = self._conn.execute(
            """\
            INSERT OR IGNORE INTO assets
                (id, schema_version, type, mime_type, extension,
                 name_text, name_normalized, size_bytes,
                 ts_modified, ts_created, storage_name, storage_mode,
                 raw_entry, ingested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.schema_version,
                record.type,
                record.mime_type,
                record.extension,
                record.name_text,
                record.name_normalized,
                record.size_bytes,
                _datetime_to_iso(record.ts_modified),
                _datetime_to_iso(record.ts_created),
                record.storage_name,
                record.storage_mode,
                json.dumps(record.raw_entry),
                _datetime_to_iso(record.ingested_at),
            ),
        )
        is_new = cursor.rowcount == 1
        if is_new:
            self._conn.execute(
                "INSERT INTO assets_fts(id, name_text, search_text) VALUES (?, ?, ?)",
                (record.id, record.name_text or "", search_text or ""),
            )
        self._conn.commit()
        return is_new

    def get_by_id(self, asset_id: str) -> AssetRecord | None:
        row = self._conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
        if row is None:
            return None
        return _row_to_record(row)

    def get_by_storage_name(self, storage_name: str) -> AssetRecord | None:
        row = self._conn.execute(
            "SELECT * FROM assets WHERE storage_name = ?", (storage_name,)
        ).fetchone()
        if row is None:
            return None
        return _row_to_record(row)

    def search(self, query: SearchQuery) -> SearchResult:
        conditions: list[str] = []
        params: list[object] = []

        if query.text_query is not None:
            conditions.append("a.id IN (SELECT id FROM assets_fts WHERE assets_fts MATCH ?)")
            params.append(query.text_query)

        if query.mime_type is not None:
            conditions.append("a.mime_type = ?")
            params.append(query.mime_type)

        if query.mime_prefix is not None:
            conditions.append("a.mime_type LIKE ? ESCAPE '\\'")
            escaped = (
                query.mime_prefix.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            )
            params.append(f"{escaped}%")

        if query.extension is not None:
            conditions.append("a.extension = ?")
            params.append(query.extension)

        if query.type is not None:
            conditions.append("a.type = ?")
            params.append(query.type)

        if query.size_min is not None:
            conditions.append("a.size_bytes >= ?")
            params.append(query.size_min)

        if query.size_max is not None:
            conditions.append("a.size_bytes <= ?")
            params.append(query.size_max)

        if query.modified_after is not None:
            conditions.append("a.ts_modified > ?")
            params.append(_datetime_to_iso(query.modified_after))

        if query.modified_before is not None:
            conditions.append("a.ts_modified < ?")
            params.append(_datetime_to_iso(query.modified_before))

        if query.name_contains is not None:
            conditions.append("a.name_normalized LIKE ? ESCAPE '\\'")
            escaped = (
                query.name_contains.lower()
                .replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            params.append(f"%{escaped}%")

        where = " AND ".join(conditions) if conditions else "1=1"

        count_sql = f"SELECT COUNT(*) FROM assets a WHERE {where}"
        total = self._conn.execute(count_sql, params).fetchone()[0]

        select_sql = (
            f"SELECT a.* FROM assets a WHERE {where} ORDER BY a.ingested_at DESC LIMIT ? OFFSET ?"
        )
        rows = self._conn.execute(select_sql, [*params, query.limit, query.offset]).fetchall()

        items = tuple(_row_to_record(r) for r in rows)
        return SearchResult(items=items, total=total, query=query)

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]

    def iter_all_storage_names(self) -> Iterator[str]:
        cursor = self._conn.execute("SELECT storage_name FROM assets ORDER BY storage_name")
        for row in cursor:
            yield row["storage_name"]

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
