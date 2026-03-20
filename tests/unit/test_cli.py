"""Unit tests for CLI subcommands (§12)."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from metadexer.cli import main


@pytest.fixture()
def runner():
    return CliRunner()


class TestHelpAndVersion:
    def test_main_help(self, runner):
        """Top-level --help exits 0 and shows group help."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Content-addressed asset management" in result.output

    def test_version(self, runner):
        """--version exits 0 and prints the version string."""
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "metadexer" in result.output

    def test_ingest_help(self, runner):
        """ingest --help exits 0 and describes the target argument."""
        result = runner.invoke(main, ["ingest", "--help"])
        assert result.exit_code == 0
        assert "TARGET" in result.output

    def test_search_help(self, runner):
        """search --help exits 0 and shows filter options."""
        result = runner.invoke(main, ["search", "--help"])
        assert result.exit_code == 0
        assert "--mime-type" in result.output

    def test_vault_help(self, runner):
        """vault --help exits 0 and lists vault subcommands."""
        result = runner.invoke(main, ["vault", "--help"])
        assert result.exit_code == 0
        assert "verify" in result.output

    def test_config_help(self, runner):
        """config --help exits 0 and lists config subcommands."""
        result = runner.invoke(main, ["config", "--help"])
        assert result.exit_code == 0
        assert "show" in result.output


class TestIngestCommand:
    def test_ingest_nonexistent_target(self, runner):
        """ingest with nonexistent path exits with error."""
        result = runner.invoke(main, ["ingest", "/nonexistent/path/xyz"])
        assert result.exit_code != 0

    def test_ingest_success(self, runner, tmp_path):
        """ingest with valid target runs pipeline and outputs JSON."""
        from metadexer.sync.pipeline import SyncResult

        test_result = SyncResult(
            indexed=2,
            new_vault=1,
            new_inline=1,
            duplicate=0,
            failed=0,
            errors=(),
        )

        target_dir = tmp_path / "input"
        target_dir.mkdir()

        mock_pipeline = MagicMock()
        mock_pipeline.ingest.return_value = test_result

        with (
            patch("metadexer.cli.load_config") as mock_load,
            patch("metadexer.cli._create_backends") as mock_backends,
            patch("metadexer.catalog.ingest.CatalogIngestor"),
            patch(
                "metadexer.sync.pipeline.SyncPipeline",
                return_value=mock_pipeline,
            ),
        ):
            from metadexer.config import MetadexerConfig

            mock_load.return_value = MetadexerConfig()
            mock_backends.return_value = (MagicMock(), MagicMock())
            result = runner.invoke(main, ["ingest", str(target_dir)])

        assert result.exit_code == 0, result.output
        assert '"indexed": 2' in result.output


class TestSearchCommand:
    def test_search_outputs_json(self, runner):
        """search command outputs JSON with total and items."""
        from metadexer.catalog import SearchQuery, SearchResult

        empty_result = SearchResult(items=(), total=0, query=SearchQuery())
        mock_searcher = MagicMock()
        mock_searcher.search.return_value = empty_result

        with (
            patch("metadexer.cli.load_config") as mock_load,
            patch("metadexer.cli._create_backends") as mock_backends,
            patch(
                "metadexer.catalog.search.CatalogSearcher",
                return_value=mock_searcher,
            ),
        ):
            from metadexer.config import MetadexerConfig

            mock_load.return_value = MetadexerConfig()
            mock_backends.return_value = (MagicMock(), MagicMock())
            result = runner.invoke(main, ["search", "test"])

        assert result.exit_code == 0
        assert '"total": 0' in result.output


class TestConfigShowCommand:
    def test_config_show_outputs_json(self, runner):
        """config show outputs resolved configuration as JSON."""
        from metadexer.config import MetadexerConfig

        with patch("metadexer.cli.load_config") as mock_load:
            mock_load.return_value = MetadexerConfig()
            result = runner.invoke(main, ["config", "show"])

        assert result.exit_code == 0
        assert '"vault"' in result.output
        assert '"catalog"' in result.output
        assert '"logging"' in result.output


class TestErrorMapping:
    def test_configuration_error_exit_code(self, runner):
        """ConfigurationError maps to exit code 2."""
        from metadexer.exceptions import ConfigurationError

        with patch("metadexer.cli.load_config") as mock_load:
            mock_load.side_effect = ConfigurationError("bad config")
            result = runner.invoke(main, ["config", "show"])

        assert result.exit_code == 2
        assert "bad config" in result.output
