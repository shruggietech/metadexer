# src/metadexer/sync/__init__.py
"""Sync module — ingestion pipeline orchestration.

Public API:
    index_target  — invoke shruggie-indexer for a single path
    SyncPipeline  — pipeline orchestrator
    SyncResult    — frozen result dataclass
"""

from __future__ import annotations

import json
import logging
import subprocess
from typing import TYPE_CHECKING

from metadexer.exceptions import IndexerInvocationError

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["index_target"]

logger = logging.getLogger(__name__)

# ── shruggie-indexer invocation (§15.1) ────────────────────────────────────

_USE_LIBRARY: bool | None = None
_index_path_fn = None


def _resolve_invocation_method() -> None:
    """Determine whether to use library import or subprocess fallback.

    Called once; result cached in module-level variables.
    """
    global _USE_LIBRARY, _index_path_fn
    try:
        from shruggie_indexer import index_path as _lib_fn  # type: ignore[import-untyped]

        _USE_LIBRARY = True
        _index_path_fn = _lib_fn
        logger.debug("shruggie-indexer: using library import")
    except ImportError:
        _USE_LIBRARY = False
        _index_path_fn = None
        logger.debug("shruggie-indexer: falling back to subprocess")


def index_target(target: Path) -> list[dict]:
    """Invoke shruggie-indexer for *target* and return IndexEntry dicts.

    Uses Python library import when available; falls back to subprocess
    invocation otherwise (§15.1).
    """
    global _USE_LIBRARY
    if _USE_LIBRARY is None:
        _resolve_invocation_method()

    if _USE_LIBRARY:
        return _index_via_library(target)
    return _index_via_subprocess(target)


def _index_via_library(target: Path) -> list[dict]:
    """Call shruggie-indexer's ``index_path`` Python API."""
    try:
        result = _index_path_fn(target)  # type: ignore[misc]
        if isinstance(result, dict):
            return [result]
        return list(result)
    except Exception as exc:
        raise IndexerInvocationError(
            f"shruggie-indexer library call failed for {target}: {exc}"
        ) from exc


def _index_via_subprocess(target: Path) -> list[dict]:
    """Shell out to the ``shruggie-indexer`` CLI with JSON output."""
    cmd = ["shruggie-indexer", "--json", str(target)]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise IndexerInvocationError("shruggie-indexer not found on PATH") from exc

    if proc.returncode != 0:
        raise IndexerInvocationError(
            f"shruggie-indexer exited with code {proc.returncode}: {proc.stderr.strip()}"
        )

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise IndexerInvocationError(f"shruggie-indexer produced unparseable JSON: {exc}") from exc

    if isinstance(data, dict):
        return [data]
    return list(data)
