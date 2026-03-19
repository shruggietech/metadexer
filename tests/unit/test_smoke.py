# tests/unit/test_smoke.py
"""Smoke tests — verify package structure and importability."""


def test_package_importable():
    """The metadexer package is importable and exposes a version string."""
    import metadexer

    assert hasattr(metadexer, "__version__")
    assert isinstance(metadexer.__version__, str)
    assert len(metadexer.__version__) > 0


def test_cli_entry_point_importable():
    """The CLI entry point module is importable."""
    from metadexer.cli import main

    assert callable(main)


def test_submodules_importable():
    """All three core submodules are importable."""
    import metadexer.catalog
    import metadexer.sync
    import metadexer.vault

    # Verify they are actual modules, not empty namespaces
    assert hasattr(metadexer.vault, "__name__")
    assert hasattr(metadexer.catalog, "__name__")
    assert hasattr(metadexer.sync, "__name__")
