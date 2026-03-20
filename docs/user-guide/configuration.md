# Configuration

metadexer uses a layered TOML configuration system. Configuration is loaded
from multiple sources with a clear override order. Most users do not need a
configuration file at all — the compiled defaults cover the common case.

## Configuration Layers

Configuration is resolved in the following order (lowest to highest priority):

1. **Compiled defaults** — Built into the `MetadexerConfig` dataclass.
2. **User config** — Platform-specific application data directory.
3. **Project-local config** — `.metadexer.toml` in or above the target directory.
4. **CLI arguments** — Highest priority; overrides everything.

Higher-priority layers override lower ones for scalar values. Nested sections
(TOML tables) are merged recursively. Sequence values (lists) are replaced
entirely by the higher-priority layer.

## Configuration File Locations

### User Config

| Platform | Path |
|----------|------|
| Windows | `%LOCALAPPDATA%\metadexer\config.toml` |
| Linux | `$XDG_CONFIG_HOME/metadexer/config.toml` (default: `~/.config/metadexer/config.toml`) |
| macOS | `~/Library/Application Support/metadexer/config.toml` |

### Project-Local Config

Place a `.metadexer.toml` file in your project root (or any parent directory).
metadexer searches upward from the current working directory.

## Configuration Reference

### `[vault]`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend` | string | `"local"` | Storage backend: `"local"` or `"s3"`. |
| `root` | string | `""` | Vault root path. Required for the local backend. |
| `chunk_size_bytes` | integer | `8388608` | Chunk size for reads/writes (8 MB). |

### `[vault.s3]`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `endpoint_url` | string | `""` | S3-compatible endpoint URL. |
| `bucket` | string | `""` | Bucket name. |
| `prefix` | string | `""` | Optional key prefix within the bucket. |
| `region` | string | `""` | AWS region (if applicable). |

Credentials are supplied via environment variables (`AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`) or instance profiles. They are never stored in
configuration files.

### `[catalog]`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend` | string | `"sqlite"` | Database backend: `"sqlite"` or `"postgres"`. |

### `[catalog.sqlite]`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `path` | string | `""` | Path to SQLite database file. Defaults to `<app_data_dir>/catalog.db`. |

### `[catalog.postgres]`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `host` | string | `"localhost"` | PostgreSQL host. |
| `port` | integer | `5432` | PostgreSQL port. |
| `dbname` | string | `"metadexer"` | Database name. |

PostgreSQL credentials are supplied via `PGUSER` and `PGPASSWORD` environment
variables, or the `METADEXER_DATABASE_URL` connection string.

### `[storage_routing]`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `inline_max_bytes` | integer | `65536` | Maximum size for inline storage (64 KB). |
| `inline_mime_prefixes` | list | `["text/"]` | MIME prefixes eligible for inline storage. |
| `inline_extra_types` | list | `["application/json"]` | Extra MIME types eligible for inline storage. |

Storage routing determines whether content is stored in the vault's file-based
backend (`"vault"` mode) or the vault's inline database surface (`"inline"`
mode). Both modes are vault-owned; the catalog stores only metadata and search
indexes.

### `[logging]`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `level` | string | `"INFO"` | Root log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `file_enabled` | boolean | `false` | Write persistent log files to `<app_data_dir>/logs/`. |

## Example Configuration

```toml
[vault]
backend = "local"
root = "/data/metadexer/vault"

[catalog]
backend = "sqlite"

[catalog.sqlite]
path = "/data/metadexer/catalog.db"

[storage_routing]
inline_max_bytes = 65536
inline_mime_prefixes = ["text/"]
inline_extra_types = ["application/json"]

[logging]
level = "INFO"
```

## Viewing Resolved Configuration

Use the `config show` command to display the fully resolved configuration:

```bash
metadexer config show
```

This outputs JSON showing the effective configuration after all layers have
been applied. Unknown keys in TOML files are silently ignored for forward
compatibility.
