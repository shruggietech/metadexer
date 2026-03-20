# src/metadexer/sync/pipeline.py
"""Sync pipeline orchestration logic (§7.2)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from metadexer.exceptions import (
    CatalogIngestError,
    IndexerInvocationError,
    SyncPipelineError,
    VaultError,
)
from metadexer.sync.plan import determine_storage_mode, read_inline_content

if TYPE_CHECKING:
    from collections.abc import Callable

    from metadexer.catalog.ingest import CatalogIngestor
    from metadexer.config import StorageRoutingConfig
    from metadexer.vault.store import VaultStore

__all__ = ["SyncPipeline", "SyncResult"]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SyncResult:
    """Result of a pipeline ingest run."""

    indexed: int
    new_vault: int
    new_inline: int
    duplicate: int
    failed: int
    errors: tuple[tuple[str, str], ...]


class SyncPipeline:
    """Basic ingest pipeline per §7.2.

    Orchestrates indexer invocation, storage routing, vault storage,
    and catalog commits.
    """

    def __init__(
        self,
        vault: VaultStore,
        ingestor: CatalogIngestor,
        routing_config: StorageRoutingConfig,
        index_fn: Callable[[Path], list[dict]] | None = None,
    ) -> None:
        self._vault = vault
        self._ingestor = ingestor
        self._routing_config = routing_config
        if index_fn is None:
            from metadexer.sync import index_target

            self._index_fn = index_target
        else:
            self._index_fn = index_fn

    def ingest(self, target: Path) -> SyncResult:
        """Run the full ingest pipeline for *target*.

        Stages (§7.2):
        1. Invoke indexer to produce IndexEntry records.
        2. For each entry, apply storage routing.
        3. Store content in the appropriate vault surface.
        4. Commit metadata to the catalog.
        """
        try:
            raw_entries = self._index_fn(target)
        except IndexerInvocationError:
            raise
        except Exception as exc:
            raise SyncPipelineError(f"Failed to index target {target}: {exc}") from exc

        indexed = len(raw_entries)
        new_vault = 0
        new_inline = 0
        duplicate = 0
        failed = 0
        errors: list[tuple[str, str]] = []

        for raw_entry in raw_entries:
            entry_id = str(raw_entry.get("id", "<unknown>"))
            try:
                mode = determine_storage_mode(raw_entry, self._routing_config)
                storage_name = raw_entry["attributes"]["storage_name"]
                source_path = raw_entry.get("source_path")
                search_text: str | None = None

                if mode == "inline":
                    text_content = self._read_content(raw_entry, source_path)
                    if text_content is not None:
                        self._vault.put_inline(storage_name, text_content)
                        search_text = text_content
                    else:
                        # Fall back to vault if content can't be read as text
                        mode = "vault"

                if mode == "vault" and source_path is not None:
                    self._vault.put(storage_name, Path(source_path))

                is_new = self._ingestor.ingest(raw_entry, mode, search_text=search_text)

                if is_new:
                    if mode == "inline":
                        new_inline += 1
                    else:
                        new_vault += 1
                else:
                    duplicate += 1

            except (VaultError, CatalogIngestError) as exc:
                failed += 1
                errors.append((entry_id, str(exc)))
                logger.warning("Failed to process entry %s: %s", entry_id, exc)
            except KeyError as exc:
                failed += 1
                errors.append((entry_id, f"Missing key: {exc}"))
                logger.warning("Missing key in entry %s: %s", entry_id, exc)

        return SyncResult(
            indexed=indexed,
            new_vault=new_vault,
            new_inline=new_inline,
            duplicate=duplicate,
            failed=failed,
            errors=tuple(errors),
        )

    def _read_content(self, raw_entry: dict, source_path: str | None) -> str | None:
        """Read text content for inline storage."""
        if source_path is not None:
            return read_inline_content(
                Path(source_path),
                self._routing_config.inline_max_bytes,
            )
        # If inline_content is provided directly (e.g. from tests)
        return raw_entry.get("inline_content")
