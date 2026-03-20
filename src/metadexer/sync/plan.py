# src/metadexer/sync/plan.py
"""Storage routing and Sync Plan generation (§6.5, §7.3)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from metadexer.config import StorageRoutingConfig

__all__ = ["determine_storage_mode", "read_inline_content"]

logger = logging.getLogger(__name__)


def determine_storage_mode(raw_entry: dict, config: StorageRoutingConfig) -> str:
    """Return ``'vault'`` or ``'inline'``. Both are vault-owned surfaces.

    Applies the storage routing rules from §6.5:
    1. MIME type eligibility — only configured prefixes/extras are inline-eligible.
    2. Size threshold — eligible content must be ≤ ``inline_max_bytes``.
    """
    mime_type: str = raw_entry.get("mime_type") or ""
    size_bytes: int = raw_entry.get("size", {}).get("bytes", 0)

    if not _mime_eligible(mime_type, config):
        return "vault"

    if size_bytes > config.inline_max_bytes:
        return "vault"

    return "inline"


def _mime_eligible(mime_type: str, config: StorageRoutingConfig) -> bool:
    """Return True if *mime_type* is eligible for inline storage."""
    if not mime_type:
        return False
    for prefix in config.inline_mime_prefixes:
        if mime_type.startswith(prefix):
            return True
    return mime_type in config.inline_extra_types


def read_inline_content(source_path: Path, max_bytes: int) -> str | None:
    """Read text content from *source_path* for inline storage.

    Returns the file's UTF-8 text if it can be decoded, or ``None`` on failure.
    Only reads up to *max_bytes* of the file.
    """
    try:
        raw = source_path.read_bytes()[:max_bytes]
        return raw.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        logger.debug("Cannot read inline content from %s", source_path)
        return None
