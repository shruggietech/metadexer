# src/metadexer/cli.py
"""CLI entry point for metadexer."""

import click

from metadexer._version import __version__


@click.group()
@click.version_option(version=__version__, prog_name="metadexer")
def main() -> None:
    """Content-addressed asset management with deep metadata search."""


if __name__ == "__main__":
    main()
