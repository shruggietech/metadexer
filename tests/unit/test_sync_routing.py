"""Unit tests for storage routing (§6.5)."""

import pytest

from metadexer.config import StorageRoutingConfig
from metadexer.sync.plan import determine_storage_mode, read_inline_content


@pytest.fixture()
def default_config():
    """Default StorageRoutingConfig matching §13.3 defaults."""
    return StorageRoutingConfig()


class TestDetermineStorageMode:
    def test_text_plain_small_is_inline(self, default_config):
        entry = {"mime_type": "text/plain", "size": {"bytes": 100}}
        assert determine_storage_mode(entry, default_config) == "inline"

    def test_text_html_small_is_inline(self, default_config):
        entry = {"mime_type": "text/html", "size": {"bytes": 1000}}
        assert determine_storage_mode(entry, default_config) == "inline"

    def test_application_json_small_is_inline(self, default_config):
        entry = {"mime_type": "application/json", "size": {"bytes": 500}}
        assert determine_storage_mode(entry, default_config) == "inline"

    def test_text_plain_over_threshold_is_vault(self, default_config):
        entry = {"mime_type": "text/plain", "size": {"bytes": 65_537}}
        assert determine_storage_mode(entry, default_config) == "vault"

    def test_text_plain_at_threshold_is_inline(self, default_config):
        entry = {"mime_type": "text/plain", "size": {"bytes": 65_536}}
        assert determine_storage_mode(entry, default_config) == "inline"

    def test_binary_type_is_vault(self, default_config):
        entry = {"mime_type": "image/jpeg", "size": {"bytes": 100}}
        assert determine_storage_mode(entry, default_config) == "vault"

    def test_no_mime_type_is_vault(self, default_config):
        entry = {"mime_type": None, "size": {"bytes": 100}}
        assert determine_storage_mode(entry, default_config) == "vault"

    def test_empty_mime_type_is_vault(self, default_config):
        entry = {"mime_type": "", "size": {"bytes": 100}}
        assert determine_storage_mode(entry, default_config) == "vault"

    def test_custom_config_extra_types(self):
        config = StorageRoutingConfig(
            inline_max_bytes=1024,
            inline_mime_prefixes=("text/",),
            inline_extra_types=("application/xml",),
        )
        entry = {"mime_type": "application/xml", "size": {"bytes": 500}}
        assert determine_storage_mode(entry, config) == "inline"

    def test_custom_config_reduced_threshold(self):
        config = StorageRoutingConfig(inline_max_bytes=50)
        entry = {"mime_type": "text/plain", "size": {"bytes": 100}}
        assert determine_storage_mode(entry, config) == "vault"


class TestReadInlineContent:
    def test_reads_utf8_file(self, tmp_path):
        p = tmp_path / "hello.txt"
        p.write_text("hello world", encoding="utf-8")
        result = read_inline_content(p, 65_536)
        assert result == "hello world"

    def test_respects_max_bytes(self, tmp_path):
        p = tmp_path / "big.txt"
        p.write_text("a" * 200, encoding="utf-8")
        result = read_inline_content(p, 100)
        assert result == "a" * 100

    def test_returns_none_for_binary(self, tmp_path):
        p = tmp_path / "binary.bin"
        p.write_bytes(b"\x80\x81\x82\x83")
        result = read_inline_content(p, 65_536)
        assert result is None

    def test_returns_none_for_missing_file(self, tmp_path):
        p = tmp_path / "nonexistent.txt"
        result = read_inline_content(p, 65_536)
        assert result is None
