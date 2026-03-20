"""PostgreSQL catalog backend (§6.4.1 and §6.8.1)."""

import json
import logging
from collections.abc import Iterator

import psycopg
from psycopg.rows import dict_row

from metadexer.catalog import AssetRecord, SearchQuery, SearchResult
from metadexer.catalog.backends import CatalogBackend
from metadexer.exceptions import CatalogConnectionError, CatalogSchemaError

logger = logging.getLogger(__name__)

__all__ = ["PostgresCatalogBackend"]

_CREATE_ASSETS_TABLE = """\
CREATE TABLE IF NOT EXISTS assets (
    id              TEXT        NOT NULL,
    schema_version  INTEGER     NOT NULL,
    type            TEXT        NOT NULL,
    mime_type       TEXT,
    extension       TEXT,
    name_text       TEXT,
    name_normalized TEXT,
    size_bytes      BIGINT,
    ts_modified     TIMESTAMPTZ,
    ts_created      TIMESTAMPTZ,
    storage_name    TEXT        NOT NULL,
    storage_mode    TEXT        NOT NULL CHECK (storage_mode IN ('vault', 'inline')),
    raw_entry       JSONB       NOT NULL,
    search_vector   TSVECTOR,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_assets PRIMARY KEY (id),
    CONSTRAINT uq_assets_storage_name UNIQUE (storage_name)
);
"""

_CREATE_INDEXES = """\
CREATE INDEX IF NOT EXISTS idx_assets_mime_type   ON assets (mime_type);
CREATE INDEX IF NOT EXISTS idx_assets_extension   ON assets (extension);
CREATE INDEX IF NOT EXISTS idx_assets_size_bytes  ON assets (size_bytes);
CREATE INDEX IF NOT EXISTS idx_assets_ts_modified ON assets (ts_modified);
CREATE INDEX IF NOT EXISTS idx_assets_name_text
    ON assets USING gin (to_tsvector('simple', name_text));
CREATE INDEX IF NOT EXISTS idx_assets_search      ON assets USING gin (search_vector);
"""

_UPSERT_SQL = """\
INSERT INTO assets (
    id, schema_version, type, mime_type, extension,
    name_text, name_normalized, size_bytes,
    ts_modified, ts_created, storage_name, storage_mode,
    raw_entry, search_vector, ingested_at
) VALUES (
    %(id)s, %(schema_version)s, %(type)s, %(mime_type)s, %(extension)s,
    %(name_text)s, %(name_normalized)s, %(size_bytes)s,
    %(ts_modified)s, %(ts_created)s, %(storage_name)s, %(storage_mode)s,
    %(raw_entry)s,
    setweight(to_tsvector('simple', COALESCE(%(name_text)s, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(%(search_text)s, '')), 'B'),
    %(ingested_at)s
)
ON CONFLICT (id) DO NOTHING
"""


def _row_to_record(row: dict) -> AssetRecord:
    raw = row["raw_entry"]
    if isinstance(raw, str):
        raw = json.loads(raw)
    return AssetRecord(
        id=row["id"],
        schema_version=row["schema_version"],
        type=row["type"],
        mime_type=row["mime_type"],
        extension=row["extension"],
        name_text=row["name_text"],
        name_normalized=row["name_normalized"],
        size_bytes=row["size_bytes"],
        ts_modified=row["ts_modified"],
        ts_created=row["ts_created"],
        storage_name=row["storage_name"],
        storage_mode=row["storage_mode"],
        raw_entry=raw,
        ingested_at=row["ingested_at"],
    )


class PostgresCatalogBackend(CatalogBackend):
    """PostgreSQL implementation of the CatalogBackend interface."""

    def __init__(self, dsn: str) -> None:
        try:
            self._conn = psycopg.connect(dsn, row_factory=dict_row, autocommit=False)
        except psycopg.Error as exc:
            raise CatalogConnectionError(f"Failed to connect to PostgreSQL: {exc}") from exc

    @property
    def connection(self) -> psycopg.Connection:
        """Expose the underlying connection for VaultInlineStore co-location."""
        return self._conn

    def initialize_schema(self) -> None:
        try:
            with self._conn.cursor() as cur:
                cur.execute(_CREATE_ASSETS_TABLE)
                for stmt in _CREATE_INDEXES.strip().split("\n"):
                    stmt = stmt.strip()
                    if stmt:
                        cur.execute(stmt)
            self._conn.commit()
        except psycopg.Error as exc:
            self._conn.rollback()
            raise CatalogSchemaError("Failed to initialize PostgreSQL catalog schema") from exc

    def upsert_asset(self, record: AssetRecord, search_text: str | None = None) -> bool:
        params = {
            "id": record.id,
            "schema_version": record.schema_version,
            "type": record.type,
            "mime_type": record.mime_type,
            "extension": record.extension,
            "name_text": record.name_text,
            "name_normalized": record.name_normalized,
            "size_bytes": record.size_bytes,
            "ts_modified": record.ts_modified,
            "ts_created": record.ts_created,
            "storage_name": record.storage_name,
            "storage_mode": record.storage_mode,
            "raw_entry": psycopg.types.json.Jsonb(record.raw_entry),
            "search_text": search_text or "",
            "ingested_at": record.ingested_at,
        }
        with self._conn.cursor() as cur:
            cur.execute(_UPSERT_SQL, params)
            is_new = cur.rowcount == 1
        self._conn.commit()
        return is_new

    def get_by_id(self, asset_id: str) -> AssetRecord | None:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM assets WHERE id = %(id)s",
                {"id": asset_id},
            )
            row = cur.fetchone()
        if row is None:
            return None
        return _row_to_record(row)

    def get_by_storage_name(self, storage_name: str) -> AssetRecord | None:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM assets WHERE storage_name = %(sn)s",
                {"sn": storage_name},
            )
            row = cur.fetchone()
        if row is None:
            return None
        return _row_to_record(row)

    def search(self, query: SearchQuery) -> SearchResult:
        conditions: list[str] = []
        params: dict[str, object] = {}

        if query.text_query is not None:
            conditions.append("a.search_vector @@ plainto_tsquery('simple', %(text_query)s)")
            params["text_query"] = query.text_query

        if query.mime_type is not None:
            conditions.append("a.mime_type = %(mime_type)s")
            params["mime_type"] = query.mime_type

        if query.mime_prefix is not None:
            conditions.append("a.mime_type LIKE %(mime_prefix)s")
            params["mime_prefix"] = f"{query.mime_prefix}%"

        if query.extension is not None:
            conditions.append("a.extension = %(extension)s")
            params["extension"] = query.extension

        if query.type is not None:
            conditions.append("a.type = %(type)s")
            params["type"] = query.type

        if query.size_min is not None:
            conditions.append("a.size_bytes >= %(size_min)s")
            params["size_min"] = query.size_min

        if query.size_max is not None:
            conditions.append("a.size_bytes <= %(size_max)s")
            params["size_max"] = query.size_max

        if query.modified_after is not None:
            conditions.append("a.ts_modified > %(modified_after)s")
            params["modified_after"] = query.modified_after

        if query.modified_before is not None:
            conditions.append("a.ts_modified < %(modified_before)s")
            params["modified_before"] = query.modified_before

        if query.name_contains is not None:
            conditions.append("a.name_normalized LIKE %(name_contains)s")
            params["name_contains"] = f"%{query.name_contains.lower()}%"

        where = " AND ".join(conditions) if conditions else "1=1"

        with self._conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS cnt FROM assets a WHERE {where}",
                params,
            )
            total = cur.fetchone()["cnt"]

            cur.execute(
                f"SELECT a.* FROM assets a WHERE {where} "
                "ORDER BY a.ingested_at DESC LIMIT %(limit)s OFFSET %(offset)s",
                {**params, "limit": query.limit, "offset": query.offset},
            )
            rows = cur.fetchall()

        items = tuple(_row_to_record(r) for r in rows)
        return SearchResult(items=items, total=total, query=query)

    def count(self) -> int:
        with self._conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM assets")
            return cur.fetchone()["cnt"]

    def iter_all_storage_names(self) -> Iterator[str]:
        with self._conn.cursor() as cur:
            cur.execute("SELECT storage_name FROM assets ORDER BY storage_name")
            for row in cur:
                yield row["storage_name"]

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
