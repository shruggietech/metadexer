"""Shared fixtures for integration tests."""

import os

import pytest

try:
    from metadexer.catalog.backends.postgres import PostgresCatalogBackend
except ImportError:
    PostgresCatalogBackend = None


@pytest.fixture(scope="session")
def pg_dsn():
    """Read the PostgreSQL DSN from the environment, skip if unset."""
    dsn = os.environ.get("METADEXER_TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("METADEXER_TEST_DATABASE_URL not set — skipping PostgreSQL tests")
    return dsn


@pytest.fixture()
def pg_backend(pg_dsn):
    """Create a PostgresCatalogBackend, initialize schema, and clean up between tests."""
    backend = PostgresCatalogBackend(pg_dsn)
    backend.initialize_schema()
    yield backend
    # Truncate tables between tests to ensure isolation
    with backend.connection.cursor() as cur:
        cur.execute("TRUNCATE TABLE assets CASCADE")
        # vault_inline may not exist yet; ignore errors
        try:
            cur.execute("TRUNCATE TABLE vault_inline CASCADE")
        except Exception:
            backend.connection.rollback()
        else:
            backend.connection.commit()
    backend.close()
