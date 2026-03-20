# src/metadexer/cli.py
"""CLI entry point for metadexer (§12)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import click

from metadexer._version import __version__
from metadexer.config import load_config
from metadexer.exceptions import (
    CatalogError,
    ConfigurationError,
    MetadexerError,
    SyncError,
    VaultError,
)

if TYPE_CHECKING:
    from metadexer.catalog.backends import CatalogBackend
    from metadexer.vault.store import VaultStore

logger = logging.getLogger(__name__)

# ── Exit code mapping (§9.3.1) ─────────────────────────────────────────────

_EXIT_CONFIG = 2
_EXIT_VAULT = 3
_EXIT_CATALOG = 4
_EXIT_SYNC = 5
_EXIT_UNEXPECTED = 1


def _exit_code_for(exc: MetadexerError) -> int:
    """Map a MetadexerError subtype to its CLI exit code."""
    if isinstance(exc, ConfigurationError):
        return _EXIT_CONFIG
    if isinstance(exc, VaultError):
        return _EXIT_VAULT
    if isinstance(exc, CatalogError):
        return _EXIT_CATALOG
    if isinstance(exc, SyncError):
        return _EXIT_SYNC
    return _EXIT_UNEXPECTED


# ── Backend instantiation helper ────────────────────────────────────────────


def _create_backends(
    config: object,
) -> tuple[VaultStore, CatalogBackend]:
    """Create vault and catalog backends from configuration.

    Returns ``(VaultStore, CatalogBackend)``.
    """
    from metadexer.config import MetadexerConfig
    from metadexer.vault.inline import VaultInlineStore
    from metadexer.vault.store import VaultStore as _VaultStore

    cfg: MetadexerConfig = config  # type: ignore[assignment]

    # 1. Create catalog backend
    if cfg.catalog.backend == "postgres":
        from metadexer.catalog.backends.postgres import PostgresCatalogBackend

        pg = cfg.catalog.postgres
        dsn = f"host={pg.host} port={pg.port} dbname={pg.dbname}"
        catalog_backend = PostgresCatalogBackend(dsn)
    else:
        from metadexer.catalog.backends.sqlite import SqliteCatalogBackend

        db_path = cfg.catalog.sqlite.path
        if not db_path:
            from metadexer.config import get_app_data_dir

            db_path = str(get_app_data_dir() / "catalog.db")
        catalog_backend = SqliteCatalogBackend(Path(db_path))

    # 2. Create VaultInlineStore from catalog backend's connection
    if cfg.catalog.backend == "postgres":
        inline_store = VaultInlineStore.from_postgres(catalog_backend.connection)
    else:
        inline_store = VaultInlineStore.from_sqlite(catalog_backend.connection)

    # 3. Initialize both schemas
    catalog_backend.initialize_schema()
    inline_store.initialize_schema()

    # 4. Create file-based vault backend
    if cfg.vault.backend == "s3":
        from metadexer.vault.backends.s3 import S3VaultBackend

        file_backend = S3VaultBackend(
            endpoint_url=cfg.vault.s3.endpoint_url,
            bucket=cfg.vault.s3.bucket,
            prefix=cfg.vault.s3.prefix,
            region=cfg.vault.s3.region,
            chunk_size=cfg.vault.chunk_size_bytes,
        )
    else:
        from metadexer.vault.backends.local import LocalVaultBackend

        vault_root = cfg.vault.root
        if not vault_root:
            raise ConfigurationError("vault.root must be set when using the local backend")
        file_backend = LocalVaultBackend(
            root=Path(vault_root),
            chunk_size=cfg.vault.chunk_size_bytes,
        )

    # 5. Assemble VaultStore
    vault = _VaultStore(
        backend=file_backend,
        chunk_size=cfg.vault.chunk_size_bytes,
        inline_store=inline_store,
    )

    return vault, catalog_backend


# ── CLI groups and commands ─────────────────────────────────────────────────


@click.group()
@click.version_option(version=__version__, prog_name="metadexer")
@click.option(
    "--config-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Project directory for config file discovery.",
)
@click.pass_context
def main(ctx: click.Context, config_dir: Path | None) -> None:
    """Content-addressed asset management with deep metadata search."""
    ctx.ensure_object(dict)
    ctx.obj["config_dir"] = config_dir


@main.command()
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def ingest(ctx: click.Context, target: Path) -> None:
    """Run the sync pipeline on a target directory or file."""
    from metadexer.catalog.ingest import CatalogIngestor
    from metadexer.sync.pipeline import SyncPipeline

    try:
        config = load_config(project_dir=ctx.obj.get("config_dir"))
        vault, catalog_backend = _create_backends(config)
        ingestor = CatalogIngestor(catalog_backend)
        pipeline = SyncPipeline(
            vault=vault,
            ingestor=ingestor,
            routing_config=config.storage_routing,
        )
        result = pipeline.ingest(target)
        output = {
            "indexed": result.indexed,
            "new_vault": result.new_vault,
            "new_inline": result.new_inline,
            "duplicate": result.duplicate,
            "failed": result.failed,
            "errors": [{"id": e[0], "message": e[1]} for e in result.errors],
        }
        click.echo(json.dumps(output, indent=2))
    except MetadexerError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(_exit_code_for(exc)) from None


@main.command()
@click.argument("query", default="")
@click.option("--mime-type", default=None, help="Filter by exact MIME type.")
@click.option("--extension", default=None, help="Filter by file extension (no dot).")
@click.option("--type", "asset_type", default=None, help="Filter by asset type (file/directory).")
@click.option("--limit", default=100, type=int, help="Maximum results to return.")
@click.option("--offset", default=0, type=int, help="Pagination offset.")
@click.pass_context
def search(
    ctx: click.Context,
    query: str,
    mime_type: str | None,
    extension: str | None,
    asset_type: str | None,
    limit: int,
    offset: int,
) -> None:
    """Query the catalog for matching assets."""
    from metadexer.catalog import SearchQuery
    from metadexer.catalog.search import CatalogSearcher

    try:
        config = load_config(project_dir=ctx.obj.get("config_dir"))
        _vault, catalog_backend = _create_backends(config)
        searcher = CatalogSearcher(catalog_backend)
        sq = SearchQuery(
            text_query=query if query else None,
            mime_type=mime_type,
            extension=extension,
            type=asset_type,
            limit=limit,
            offset=offset,
        )
        result = searcher.search(sq)
        output = {
            "total": result.total,
            "items": [
                {
                    "id": r.id,
                    "name": r.name_text,
                    "mime_type": r.mime_type,
                    "extension": r.extension,
                    "size_bytes": r.size_bytes,
                    "storage_name": r.storage_name,
                    "storage_mode": r.storage_mode,
                }
                for r in result.items
            ],
        }
        click.echo(json.dumps(output, indent=2))
    except MetadexerError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(_exit_code_for(exc)) from None


# ── vault subgroup ──────────────────────────────────────────────────────────


@main.group()
def vault() -> None:
    """Vault operations (verify, prune)."""


@vault.command()
@click.option(
    "--storage-name",
    required=True,
    help="The storage_name of the object to verify.",
)
@click.option(
    "--hash",
    "hash_pairs",
    multiple=True,
    type=(str, str),
    help="Algorithm and expected hex digest pair, e.g. --hash sha256 ABCD1234.",
)
@click.pass_context
def verify(ctx: click.Context, storage_name: str, hash_pairs: tuple[tuple[str, str], ...]) -> None:
    """Re-hash stored bytes and compare against expected hashes."""
    try:
        config = load_config(project_dir=ctx.obj.get("config_dir"))
        vault_store, _catalog_backend = _create_backends(config)
        expected_hashes = {algo: digest for algo, digest in hash_pairs}
        if not expected_hashes:
            record = _catalog_backend.get_by_storage_name(storage_name)
            if record and record.raw_entry.get("hashes"):
                expected_hashes = record.raw_entry["hashes"]
            else:
                click.echo("No hashes provided and none found in catalog.", err=True)
                raise SystemExit(_EXIT_VAULT)
        result = vault_store.verify(storage_name, expected_hashes)
        output = {
            "storage_name": result.storage_name,
            "passed": result.passed,
            "checked": result.checked,
            "expected": result.expected,
            "actual": result.actual,
        }
        click.echo(json.dumps(output, indent=2))
        if not result.passed:
            raise SystemExit(_EXIT_VAULT)
    except MetadexerError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(_exit_code_for(exc)) from None


# ── config subgroup ─────────────────────────────────────────────────────────


@main.group("config")
def config_group() -> None:
    """Configuration management."""


@config_group.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Display the resolved configuration."""
    from dataclasses import asdict

    try:
        config = load_config(project_dir=ctx.obj.get("config_dir"))
        data = asdict(config)
        # Convert tuples to lists for JSON serialization
        _tuples_to_lists(data)
        click.echo(json.dumps(data, indent=2))
    except MetadexerError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(_exit_code_for(exc)) from None


def _tuples_to_lists(obj: object) -> None:
    """Recursively convert tuple values to lists in a dict for JSON output."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, tuple):
                obj[key] = list(val)
            elif isinstance(val, dict):
                _tuples_to_lists(val)


if __name__ == "__main__":
    main()
