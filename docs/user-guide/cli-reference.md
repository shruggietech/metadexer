# CLI Reference

The `metadexer` command-line interface provides subcommands for ingesting files,
querying the catalog, verifying vault integrity, and inspecting configuration.

All structured output is emitted to `stdout` as JSON. Diagnostic messages and
errors are written to `stderr`. This convention allows scripts and pipelines to
parse output reliably.

## Command Tree

```
metadexer [OPTIONS] COMMAND [ARGS]
```

### Global Options

| Option | Description |
|--------|-------------|
| `--version` | Print the version string and exit. |
| `--config-dir PATH` | Project directory for config file discovery. |
| `--help` | Show help message and exit. |

---

## `metadexer ingest`

Run the sync pipeline on a target directory or file.

```
metadexer ingest TARGET
```

**Arguments:**

- `TARGET` — Path to a file or directory to ingest. Must exist.

**Output (JSON):**

```json
{
  "indexed": 10,
  "new_vault": 3,
  "new_inline": 5,
  "duplicate": 2,
  "failed": 0,
  "errors": []
}
```

**Storage modes:** The `new_vault` and `new_inline` counters reflect the two
vault-owned storage surfaces. `"vault"` indicates file-based storage in the
local or S3 backend. `"inline"` indicates text content stored in the vault's
inline database surface. Both are managed by the vault module; the catalog
stores only metadata and search indexes.

---

## `metadexer search`

Query the catalog for matching assets.

```
metadexer search [QUERY] [OPTIONS]
```

**Arguments:**

- `QUERY` — Full-text search string (optional). Searches across file names
  and vault-stored inline text content.

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--mime-type TEXT` | string | Filter by exact MIME type. |
| `--extension TEXT` | string | Filter by file extension (no leading dot). |
| `--type TEXT` | string | Filter by asset type (`file` or `directory`). |
| `--limit INT` | integer | Maximum results to return (default: 100). |
| `--offset INT` | integer | Pagination offset (default: 0). |

**Output (JSON):**

```json
{
  "total": 42,
  "items": [
    {
      "id": "abc123...",
      "name": "document.txt",
      "mime_type": "text/plain",
      "extension": "txt",
      "size_bytes": 1024,
      "storage_name": "SHA256-abc123.txt",
      "storage_mode": "inline"
    }
  ]
}
```

---

## `metadexer vault`

Vault operations group.

### `metadexer vault verify`

Re-hash stored bytes and compare against expected hashes.

```
metadexer vault verify --storage-name NAME [--hash ALGO DIGEST]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--storage-name TEXT` | The storage_name of the object to verify. Required. |
| `--hash ALGO DIGEST` | Algorithm and expected hex digest pair. Repeatable. |

If no `--hash` pairs are provided, the command attempts to look up expected
hashes from the catalog record's `raw_entry.hashes` field.

**Output (JSON):**

```json
{
  "storage_name": "SHA256-abc123.txt",
  "passed": true,
  "checked": {"sha256": true},
  "expected": {"sha256": "ABCD1234..."},
  "actual": {"sha256": "ABCD1234..."}
}
```

Exits with code 3 if verification fails.

---

## `metadexer config`

Configuration management group.

### `metadexer config show`

Display the fully resolved configuration as JSON, after applying all layers
(compiled defaults, user config, project config, CLI overrides).

```
metadexer config show
```

**Output (JSON):**

```json
{
  "vault": {"backend": "local", "root": "", ...},
  "catalog": {"backend": "sqlite", ...},
  "storage_routing": {"inline_max_bytes": 65536, ...},
  "logging": {"level": "INFO", "file_enabled": false}
}
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success. |
| 1 | Unexpected error (bug). |
| 2 | Configuration error (`ConfigurationError`). |
| 3 | Vault operation failed (`VaultError`). |
| 4 | Catalog operation failed (`CatalogError`). |
| 5 | Sync pipeline or indexer error (`SyncError`). |
