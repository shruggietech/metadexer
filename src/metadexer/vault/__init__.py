# src/metadexer/vault/__init__.py
"""Vault module — content-addressed storage (files and inline text)."""

from metadexer.vault.inline import VaultInlineStore
from metadexer.vault.store import PruneResult, VaultStore, VerifyResult

__all__ = ["PruneResult", "VaultInlineStore", "VaultStore", "VerifyResult"]
