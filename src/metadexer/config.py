"""Configuration loading and dataclasses (§13)."""

from __future__ import annotations

import logging
import os
import sys
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path

from metadexer.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

__all__ = [
    "CatalogConfig",
    "LoggingConfig",
    "MetadexerConfig",
    "PostgresConfig",
    "S3Config",
    "SqliteConfig",
    "StorageRoutingConfig",
    "VaultConfig",
    "get_app_data_dir",
    "load_config",
]


# ── Dataclass hierarchy (all frozen) ───────────────────────────────────────


@dataclass(frozen=True)
class S3Config:
    endpoint_url: str = ""
    bucket: str = ""
    prefix: str = ""
    region: str = ""


@dataclass(frozen=True)
class VaultConfig:
    backend: str = "local"
    root: str = ""
    chunk_size_bytes: int = 8_388_608
    s3: S3Config = field(default_factory=S3Config)


@dataclass(frozen=True)
class SqliteConfig:
    path: str = ""


@dataclass(frozen=True)
class PostgresConfig:
    host: str = "localhost"
    port: int = 5432
    dbname: str = "metadexer"


@dataclass(frozen=True)
class CatalogConfig:
    backend: str = "sqlite"
    sqlite: SqliteConfig = field(default_factory=SqliteConfig)
    postgres: PostgresConfig = field(default_factory=PostgresConfig)


@dataclass(frozen=True)
class StorageRoutingConfig:
    inline_max_bytes: int = 65_536
    inline_mime_prefixes: tuple[str, ...] = ("text/",)
    inline_extra_types: tuple[str, ...] = ("application/json",)


@dataclass(frozen=True)
class LoggingConfig:
    level: str = "INFO"
    file_enabled: bool = False


@dataclass(frozen=True)
class MetadexerConfig:
    vault: VaultConfig = field(default_factory=VaultConfig)
    catalog: CatalogConfig = field(default_factory=CatalogConfig)
    storage_routing: StorageRoutingConfig = field(default_factory=StorageRoutingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


# ── Platform helpers ───────────────────────────────────────────────────────


def get_app_data_dir() -> Path:
    """Return the platform-specific application data directory (§13.2).

    Creates the directory if it does not exist.
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME", "")
        base = Path(xdg) if xdg else Path.home() / ".config"

    app_dir = base / "metadexer"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


# ── Config loading ─────────────────────────────────────────────────────────

# Mapping from top-level config key → dataclass type for nested construction.
_SECTION_TYPES: dict[str, type] = {
    "vault": VaultConfig,
    "catalog": CatalogConfig,
    "storage_routing": StorageRoutingConfig,
    "logging": LoggingConfig,
}

_NESTED_TYPES: dict[str, dict[str, type]] = {
    "vault": {"s3": S3Config},
    "catalog": {"sqlite": SqliteConfig, "postgres": PostgresConfig},
}

# Fields that should be coerced from list → tuple.
_TUPLE_FIELDS: set[str] = {
    "inline_mime_prefixes",
    "inline_extra_types",
}


def load_config(
    project_dir: Path | None = None,
    cli_overrides: dict | None = None,
) -> MetadexerConfig:
    """Load configuration using the four-layer override chain (§13.1).

    Layer 1: Compiled defaults (dataclass defaults).
    Layer 2: User config at ``<app_data_dir>/config.toml``.
    Layer 3: Project-local ``.metadexer.toml``.
    Layer 4: *cli_overrides* dict.
    """
    merged: dict = {}

    # Layer 2: user config
    user_config_path = get_app_data_dir() / "config.toml"
    if user_config_path.is_file():
        merged = _merge_dicts(merged, _load_toml(user_config_path))

    # Layer 3: project-local config
    project_toml = _find_project_config(project_dir)
    if project_toml is not None:
        merged = _merge_dicts(merged, _load_toml(project_toml))

    # Layer 4: CLI overrides
    if cli_overrides:
        merged = _merge_dicts(merged, cli_overrides)

    return _dict_to_config(merged)


def _load_toml(path: Path) -> dict:
    """Read and parse a TOML file; raise ConfigurationError on syntax errors."""
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigurationError(f"TOML syntax error in {path}: {exc}") from exc


def _find_project_config(project_dir: Path | None) -> Path | None:
    """Locate ``.metadexer.toml`` in *project_dir* or by walking upward from cwd."""
    if project_dir is not None:
        candidate = project_dir / ".metadexer.toml"
        return candidate if candidate.is_file() else None

    current = Path.cwd().resolve()
    while True:
        candidate = current / ".metadexer.toml"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _merge_dicts(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base*. Returns a new dict."""
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _merge_dicts(result[key], val)
        else:
            result[key] = val
    return result


def _dict_to_config(data: dict) -> MetadexerConfig:
    """Construct a MetadexerConfig from a plain dict, ignoring unknown keys."""
    kwargs: dict = {}
    for f in fields(MetadexerConfig):
        if f.name not in data:
            continue
        section_data = data[f.name]
        if isinstance(section_data, dict):
            kwargs[f.name] = _dict_to_section(f.name, section_data)
        else:
            kwargs[f.name] = section_data
    return MetadexerConfig(**kwargs)


def _dict_to_section(section_name: str, data: dict) -> object:
    """Construct a section dataclass from a dict."""
    cls = _SECTION_TYPES.get(section_name)
    if cls is None:
        return data

    nested_map = _NESTED_TYPES.get(section_name, {})
    kwargs: dict = {}

    for f in fields(cls):
        if f.name not in data:
            continue
        val = data[f.name]
        if f.name in nested_map and isinstance(val, dict):
            kwargs[f.name] = _build_dataclass(nested_map[f.name], val)
        elif f.name in _TUPLE_FIELDS and isinstance(val, list):
            kwargs[f.name] = tuple(val)
        else:
            kwargs[f.name] = val

    return cls(**kwargs)


def _build_dataclass(cls: type, data: dict) -> object:
    """Construct a frozen dataclass from a dict, ignoring unknown keys."""
    known = {f.name for f in fields(cls)}
    return cls(**{k: v for k, v in data.items() if k in known})
