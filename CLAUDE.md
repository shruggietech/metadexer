# CLAUDE.md — metadexer Agent Context

> This file is read automatically by Claude Code at session start.
> It provides persistent project-level context for all coding sessions.
> Do not modify this file during coding sessions. Changes are made by
> the admin layer only.

## Project Identity

- **Project:** metadexer
- **Organization:** ShruggieTech LLC (https://shruggie.tech)
- **Language:** Python 3.12+
- **License:** Apache 2.0

## Repository Structure

```
metadexer/
├── .archive/           # Historical/retired documents
├── .github/            # GitHub config, CI workflows, Copilot instructions
├── .handoff/plans/     # Sprint documents (admin → coding)
├── .handoff/reports/   # Session reports and test summaries (coding → admin)
├── docs/               # MkDocs documentation site source
├── scripts/            # Dev environment setup and build scripts
├── src/metadexer/      # Python source package
│   ├── cli.py          # CLI entry point (click)
│   ├── vault/          # Content-addressed byte storage
│   ├── catalog/        # Metadata registry, search, references
│   └── sync/           # Ingestion pipeline orchestration
├── tests/              # Test suites (unit/, integration/, conformance/, platform/)
├── metadexer-spec.md   # Authoritative technical specification
└── pyproject.toml      # Build config, dependencies, tool settings
```

## Specification Authority

1. `metadexer-spec.md` (this repo) is authoritative for all metadexer behavior.
2. `shruggie-indexer-spec.md` (shruggie-indexer repo) is authoritative for IndexEntry schema and indexer behavior.
3. When any document conflicts with the specification, the specification wins.
4. Sprint documents in `.handoff/plans/` define work scope. Do not exceed their scope.

## Coding Conventions

- UTF-8 without BOM. LF line endings. Enforced by `.gitattributes`.
- `snake_case` for all Python identifiers (variables, functions, modules).
- Import ordering: stdlib, then third-party, then local. Enforced by ruff isort.
- Use `pathlib.Path` for all filesystem operations. No raw string path manipulation.
- Use the standard `logging` module. Logger names follow package structure
  (e.g., `metadexer.vault.store`).
- Line length limit: 100 characters. Enforced by ruff.
- Type hints on all public function signatures.

## Testing Conventions

- Run all tests: `pytest`
- Strict markers enforced: `--strict-markers` is configured in `pyproject.toml`.
- Tests organized by type: `tests/unit/`, `tests/integration/`, `tests/conformance/`, `tests/platform/`.
- Platform-specific tests use markers: `@pytest.mark.platform_windows`, `@pytest.mark.platform_linux`, `@pytest.mark.platform_macos`.
- Backend-specific tests use markers: `@pytest.mark.requires_postgres`, `@pytest.mark.requires_s3`.

## CLI Conventions

- Framework: `click` (argument parsing and subcommand routing).
- `stdout` is reserved for structured output (JSON). All diagnostics go to `stderr`.
- Destructive operations require explicit opt-in flags. `--dry-run` is default for prune.
- The CLI is a thin layer over the module APIs. No business logic in `cli.py`.

## Prohibitions

- **No silent data loss.** Never delete or overwrite content without explicit user confirmation.
- **No implicit deletion.** All deletion is two-phase (reference removal, then explicit prune).
- **No identity recomputation.** Content identity is produced by shruggie-indexer only.
  metadexer preserves, records, and propagates it.
- **No architectural decisions.** Do not redefine module boundaries, invent new modules,
  or change the component map without admin layer authorization.
- **No scope creep.** Implement exactly what the sprint document specifies. File observations
  about potential improvements in the session report, do not act on them.
- **No platform-conditional logic in core modules.** `vault/`, `catalog/`, and `sync/`
  must not contain `if sys.platform` or `if os.name` branches.

## Commit Conventions

- Pattern: `<module>: <imperative description>` (e.g., `vault: implement put operation for local backend`)
- One logical change per commit. Do not bundle unrelated changes.
- Sprint reference in body (optional): `Sprint: 20260310-001, Item 3`
