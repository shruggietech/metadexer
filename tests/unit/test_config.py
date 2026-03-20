"""Tests for metadexer configuration system (§13)."""

from __future__ import annotations

import dataclasses
import os
import sys
from pathlib import Path

import pytest

from metadexer.config import (
    MetadexerConfig,
    get_app_data_dir,
    load_config,
)
from metadexer.exceptions import ConfigurationError


class TestDefaultConfig:
    def test_default_vault_backend(self):
        cfg = MetadexerConfig()
        assert cfg.vault.backend == "local"

    def test_default_vault_root_empty(self):
        cfg = MetadexerConfig()
        assert cfg.vault.root == ""

    def test_default_vault_chunk_size(self):
        cfg = MetadexerConfig()
        assert cfg.vault.chunk_size_bytes == 8_388_608

    def test_default_catalog_backend(self):
        cfg = MetadexerConfig()
        assert cfg.catalog.backend == "sqlite"

    def test_default_storage_routing(self):
        cfg = MetadexerConfig()
        assert cfg.storage_routing.inline_max_bytes == 65_536
        assert cfg.storage_routing.inline_mime_prefixes == ("text/",)
        assert cfg.storage_routing.inline_extra_types == ("application/json",)

    def test_default_logging(self):
        cfg = MetadexerConfig()
        assert cfg.logging.level == "INFO"
        assert cfg.logging.file_enabled is False

    def test_default_s3(self):
        cfg = MetadexerConfig()
        assert cfg.vault.s3.endpoint_url == ""
        assert cfg.vault.s3.bucket == ""
        assert cfg.vault.s3.prefix == ""
        assert cfg.vault.s3.region == ""

    def test_default_postgres(self):
        cfg = MetadexerConfig()
        assert cfg.catalog.postgres.host == "localhost"
        assert cfg.catalog.postgres.port == 5432
        assert cfg.catalog.postgres.dbname == "metadexer"

    def test_default_sqlite(self):
        cfg = MetadexerConfig()
        assert cfg.catalog.sqlite.path == ""


class TestTomlLoading:
    def test_toml_overrides_applied(self, tmp_path, monkeypatch):
        toml_content = '[vault]\nbackend = "s3"\nroot = "/data/vault"\n'
        config_dir = tmp_path / "metadexer"
        config_dir.mkdir()
        (config_dir / "config.toml").write_text(toml_content, encoding="utf-8")
        monkeypatch.setattr("metadexer.config.get_app_data_dir", lambda: config_dir)

        cfg = load_config(project_dir=tmp_path)
        assert cfg.vault.backend == "s3"
        assert cfg.vault.root == "/data/vault"
        # Non-overridden values retain defaults
        assert cfg.vault.chunk_size_bytes == 8_388_608
        assert cfg.catalog.backend == "sqlite"


class TestLayeredOverride:
    def test_project_config_wins_over_user_config(self, tmp_path, monkeypatch):
        # Layer 2: user config
        user_dir = tmp_path / "user_config"
        user_dir.mkdir()
        (user_dir / "config.toml").write_text(
            '[vault]\nbackend = "local"\nroot = "/user/vault"\n',
            encoding="utf-8",
        )
        monkeypatch.setattr("metadexer.config.get_app_data_dir", lambda: user_dir)

        # Layer 3: project config
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".metadexer.toml").write_text(
            '[vault]\nroot = "/project/vault"\n',
            encoding="utf-8",
        )

        cfg = load_config(project_dir=project_dir)
        # Project-local wins for root
        assert cfg.vault.root == "/project/vault"
        # User config value retained where not overridden
        assert cfg.vault.backend == "local"


class TestCliOverride:
    def test_cli_override_takes_precedence(self, tmp_path, monkeypatch):
        # Layer 2: user config
        user_dir = tmp_path / "user_config"
        user_dir.mkdir()
        (user_dir / "config.toml").write_text(
            '[vault]\nroot = "/user/vault"\n',
            encoding="utf-8",
        )
        monkeypatch.setattr("metadexer.config.get_app_data_dir", lambda: user_dir)

        cfg = load_config(
            project_dir=tmp_path,
            cli_overrides={"vault": {"root": "/tmp/test"}},
        )
        assert cfg.vault.root == "/tmp/test"


class TestUnknownKeys:
    def test_unknown_keys_ignored(self, tmp_path, monkeypatch):
        toml_content = '[foo]\nbar = 1\n\n[vault]\nbackend = "local"\n'
        config_dir = tmp_path / "metadexer"
        config_dir.mkdir()
        (config_dir / "config.toml").write_text(toml_content, encoding="utf-8")
        monkeypatch.setattr("metadexer.config.get_app_data_dir", lambda: config_dir)

        cfg = load_config(project_dir=tmp_path)
        assert cfg.vault.backend == "local"


class TestSyntaxError:
    def test_invalid_toml_raises_configuration_error(self, tmp_path, monkeypatch):
        config_dir = tmp_path / "metadexer"
        config_dir.mkdir()
        (config_dir / "config.toml").write_text(
            "this is not valid toml [[[",
            encoding="utf-8",
        )
        monkeypatch.setattr("metadexer.config.get_app_data_dir", lambda: config_dir)

        with pytest.raises(ConfigurationError, match="TOML syntax error"):
            load_config(project_dir=tmp_path)


class TestFrozenImmutability:
    def test_frozen_config_raises_on_assignment(self):
        cfg = MetadexerConfig()
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.vault = None  # type: ignore[misc]

    def test_frozen_nested_raises_on_assignment(self):
        cfg = MetadexerConfig()
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.vault.backend = "s3"  # type: ignore[misc]


class TestAppDataDir:
    def test_returns_path(self):
        result = get_app_data_dir()
        assert isinstance(result, Path)

    def test_directory_exists(self):
        result = get_app_data_dir()
        assert result.is_dir()

    def test_platform_specific_root(self):
        result = get_app_data_dir()
        assert result.name == "metadexer"
        if sys.platform == "win32":
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            if local_appdata:
                assert str(result).startswith(local_appdata)
        elif sys.platform == "darwin":
            assert "Application Support" in str(result)
        else:
            # Linux/other: under XDG_CONFIG_HOME or ~/.config
            xdg = os.environ.get("XDG_CONFIG_HOME", "")
            home = str(Path.home())
            parent = str(result.parent)
            assert parent == xdg or parent == str(Path(home) / ".config")


class TestSequenceFieldsAreTuples:
    def test_inline_mime_prefixes_is_tuple(self):
        cfg = MetadexerConfig()
        assert isinstance(cfg.storage_routing.inline_mime_prefixes, tuple)

    def test_inline_extra_types_is_tuple(self):
        cfg = MetadexerConfig()
        assert isinstance(cfg.storage_routing.inline_extra_types, tuple)

    def test_tuple_from_toml(self, tmp_path, monkeypatch):
        toml_content = (
            "[storage_routing]\n"
            'inline_mime_prefixes = ["text/", "image/"]\n'
            'inline_extra_types = ["application/json", "application/xml"]\n'
        )
        config_dir = tmp_path / "metadexer"
        config_dir.mkdir()
        (config_dir / "config.toml").write_text(toml_content, encoding="utf-8")
        monkeypatch.setattr("metadexer.config.get_app_data_dir", lambda: config_dir)

        cfg = load_config(project_dir=tmp_path)
        assert isinstance(cfg.storage_routing.inline_mime_prefixes, tuple)
        assert cfg.storage_routing.inline_mime_prefixes == ("text/", "image/")
        assert isinstance(cfg.storage_routing.inline_extra_types, tuple)
        assert cfg.storage_routing.inline_extra_types == ("application/json", "application/xml")
