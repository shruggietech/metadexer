<a name="metadexer-specification-review" id="metadexer-specification-review"></a>
# Metadexer Specification Review

| **Attribute** | **Value** |
|---|---|
| Subject | `metadexer-spec.md` (revision 2026-03-09) |
| Review Date | 2026-03-19 |
| Reviewer | Claude (Admin Layer Session) |
| Purpose | Pre-Sprint 1 gap analysis for agent-readiness |

---

<a name="abstract" id="abstract"></a>

<div style="text-align:justify">

This report documents the findings of a final review pass on the metadexer technical specification. The review was conducted with a single question in mind: if a coding agent received a sprint plan referencing this specification, would the spec provide enough detail for the agent to produce correct implementations without interactive clarification? The findings are organized into two tiers: items that block Sprint 1 execution and items that can be deferred to later phases.

</div>

<hr class="print-page-break">

<a name="table-of-contents" id="table-of-contents"></a>
## Table of Contents

- [1. Summary of Findings](#1-summary-of-findings)
- [2. Sprint 1 Blockers](#2-sprint-1-blockers)
  - [2.1. Catalog Database Schema](#21-catalog-database-schema)
  - [2.2. Consolidated pyproject.toml](#22-consolidated-pyprojecttoml)
  - [2.3. Agent Context File Text](#23-agent-context-file-text)
  - [2.4. Storage Routing Default Thresholds](#24-storage-routing-default-thresholds)
  - [2.5. Vault Local Backend Directory Layout](#25-vault-local-backend-directory-layout)
  - [2.6. metadexer Configuration TOML Structure](#26-metadexer-configuration-toml-structure)
  - [2.7. shruggie-indexer Invocation Method](#27-shruggie-indexer-invocation-method)
  - [2.8. Vault get-by-id Resolution Path](#28-vault-get-by-id-resolution-path)
- [3. Deferred Items](#3-deferred-items)
  - [3.1. Sync Plan Output Format](#31-sync-plan-output-format)
  - [3.2. Resumable Sync State Persistence](#32-resumable-sync-state-persistence)
  - [3.3. Reference Model Schema](#33-reference-model-schema)
  - [3.4. Temporal Correlation Storage Model](#34-temporal-correlation-storage-model)
  - [3.5. Error Type Hierarchy](#35-error-type-hierarchy)
- [4. Minor Issues and Inconsistencies](#4-minor-issues-and-inconsistencies)
  - [4.1. License Field Contradiction](#41-license-field-contradiction)
  - [4.2. CLI Subcommand Tree Hedging](#42-cli-subcommand-tree-hedging)
  - [4.3. Changelog Copy Automation](#43-changelog-copy-automation)
- [5. Items That Are Fine](#5-items-that-are-fine)

<hr class="print-page-break">

<a name="1-summary-of-findings" id="1-summary-of-findings"></a>
## 1. Summary of Findings

<div style="text-align:justify">

The specification is strong. The architectural decomposition, module invariants, responsibility boundaries, and development workflow sections are detailed enough to guide agent implementation without ambiguity. The IndexEntry contract, composition rules, failure model, and security constraints are particularly well-specified.

The three gaps previously identified (agent context file text, pyproject.toml fields, catalog database schema) are confirmed as real blockers. This review surfaces five additional items at the same severity level, all of which would force a Phase 2 coding agent to invent details that should be specified. The deferred items (§3) are genuine gaps but fall outside Phase 2 scope and do not block Sprint 1.

</div>

| Category | Count |
|---|---|
| Sprint 1 Blockers | 8 |
| Deferred Items (Phase 3+) | 5 |
| Minor Issues | 3 |

<hr class="print-page-break">

<a name="2-sprint-1-blockers" id="2-sprint-1-blockers"></a>
## 2. Sprint 1 Blockers

<div style="text-align:justify">

These items fall within Phase 2 scope and would require a coding agent to make assumptions if left unresolved. Each entry identifies the gap, the spec section(s) involved, and what specifically needs to be added.

</div>

<a name="21-catalog-database-schema" id="21-catalog-database-schema"></a>
### 2.1. Catalog Database Schema

**Spec sections:** §6, §21.2

**Current state:** The spec defines catalog operations (ingest, search, reference, correlate, reconcile), invariants, and a list of fields that must be indexed (`id`, `mime_type`, `size.bytes`, `timestamps.modified`, `name.text`, `extension`). It does not define the actual table structure, column names, column types, relationships, or constraints for either the PostgreSQL or SQLite backend.

<div style="text-align:justify">

**What is needed:** A formal schema definition covering (at minimum) the Phase 2 scope: a primary assets table with column-level definitions for all projected IndexEntry fields, the raw IndexEntry JSON storage column, the inline content column for hybrid-routed string data, unique constraints on `id`, and the index definitions referenced in §21.2. The schema must be specified for both PostgreSQL (using native types like `JSONB`, `TSVECTOR`) and SQLite (using compatible equivalents like JSON text, FTS5 virtual tables). Without this, an agent will invent a schema, and two agents working in parallel will invent different ones.

</div>

**Previously identified:** Yes (one of the three known pre-sprint gaps).

---

<a name="22-consolidated-pyprojecttoml" id="22-consolidated-pyprojecttoml"></a>
### 2.2. Consolidated pyproject.toml

**Spec sections:** §15.1, §11.6, §17, §18

<div style="text-align:justify">

**Current state:** The spec lists known dependencies in a table (§15.1) and shows the docs optional dependency group (§11.6). It references ruff, pytest, and pyinstaller by implication through other sections. However, there is no consolidated `pyproject.toml` definition equivalent to the shruggie-indexer spec's §13.2, which provides the full canonical file content.

</div>

<div style="text-align:justify">

**What is needed:** A complete `pyproject.toml` specification including: the `[build-system]` table, `[project]` metadata fields (name, description, license, requires-python, authors, keywords, dynamic version), `[project.dependencies]` with pinned minimum versions, `[project.optional-dependencies]` for dev, docs, postgres, and s3 extras groups, `[project.scripts]` entry point, `[tool.hatch.version]` path, `[tool.pytest.ini_options]` with testpaths and custom markers, `[tool.ruff]` configuration, and `[tool.hatch.build.targets.wheel]` packages path. The shruggie-indexer spec provides a good structural template.

</div>

**Previously identified:** Yes (one of the three known pre-sprint gaps).

---

<a name="23-agent-context-file-text" id="23-agent-context-file-text"></a>
### 2.3. Agent Context File Text

**Spec sections:** §23.6.1

<div style="text-align:justify">

**Current state:** §23.6.1 defines the required content categories for `CLAUDE.md` and `.github/copilot-instructions.md` as a bulleted list (project identity, repo structure summary, spec authority hierarchy, coding conventions, testing conventions, CLI conventions, explicit prohibitions). It also notes that tool-specific preambles may differ. However, the actual text of these files is not provided.

</div>

<div style="text-align:justify">

**What is needed:** The literal file contents for both agent context files, ready to be committed to the repository. This is a prerequisite for any coding agent session, since these files are auto-loaded at session start and define the behavioral guardrails the agent operates under.

</div>

**Previously identified:** Yes (one of the three known pre-sprint gaps).

---

<a name="24-storage-routing-default-thresholds" id="24-storage-routing-default-thresholds"></a>
### 2.4. Storage Routing Default Thresholds

**Spec sections:** §6.4, §13

<div style="text-align:justify">

**Current state:** §6.4 states that hybrid storage routing is "determined by configurable rulesets" that "consider factors including file size, MIME type, and content characteristics." It gives two illustrative examples (a 500-byte JSON response goes inline; a 4 GB video goes to vault) but defines no default thresholds, no MIME type classification rules, and no concrete ruleset structure. §13 describes the configuration layer architecture but provides no example TOML keys for storage routing.

</div>

<div style="text-align:justify">

**What is needed:** A default ruleset definition specifying: the maximum byte-size threshold for inline storage (e.g., 64 KB, 256 KB, or whatever the intended default is), which MIME type categories are eligible for inline storage (presumably text-based types), whether binary content is ever eligible for inline storage regardless of size, and the TOML configuration keys that control these thresholds. An agent implementing the catalog ingest path cannot write the routing logic without these values.

</div>

**Previously identified:** No.

---

<a name="25-vault-local-backend-directory-layout" id="25-vault-local-backend-directory-layout"></a>
### 2.5. Vault Local Backend Directory Layout

**Spec sections:** §5.3, §21.3

<div style="text-align:justify">

**Current state:** §5.3 says objects are stored "in a content-addressed directory structure under a configurable vault root path." §21.3 mentions a "directory sharding strategy (e.g., first N characters of `storage_name` as subdirectory prefixes)" but frames this as an example rather than a specification. The sharding depth (N), the nesting structure (flat two-character prefix vs. multi-level), and the path construction algorithm are not defined.

</div>

<div style="text-align:justify">

**What is needed:** A concrete specification of how `storage_name` maps to a filesystem path under the vault root. For example: given a vault root of `/data/vault` and a `storage_name` of `a1b2c3d4e5f6.mp4`, what is the full storage path? Is it `/data/vault/a1/b2/a1b2c3d4e5f6.mp4`? `/data/vault/a1/a1b2c3d4e5f6.mp4`? `/data/vault/a1b2c3d4e5f6.mp4`? This directly affects the vault `put`, `get`, and `head` implementations and must be consistent across all code paths.

</div>

**Previously identified:** No.

---

<a name="26-metadexer-configuration-toml-structure" id="26-metadexer-configuration-toml-structure"></a>
### 2.6. metadexer Configuration TOML Structure

**Spec sections:** §13

<div style="text-align:justify">

**Current state:** §13 defines the four-layer configuration architecture (compiled defaults, user config, project-local config, CLI arguments) and the platform-specific data directory paths. It states that configuration objects should be frozen dataclasses and that unknown keys are silently ignored. However, unlike the shruggie-indexer spec (which provides a complete example TOML file with every configurable field), the metadexer spec does not define any configuration keys, section names, or default values.

</div>

<div style="text-align:justify">

**What is needed:** A canonical example TOML file (or at minimum a table of configuration keys with types and defaults) covering the Phase 2 configuration surface: vault backend selection and root path, catalog backend selection and connection parameters, storage routing thresholds, logging configuration, and any operational defaults (chunk size, batch size). The configuration loader is a foundational component that multiple modules depend on; its structure must be defined before implementation begins.

</div>

**Previously identified:** No.

---

<a name="27-shruggie-indexer-invocation-method" id="27-shruggie-indexer-invocation-method"></a>
### 2.7. shruggie-indexer Invocation Method

**Spec sections:** §7.2, §15.1

<div style="text-align:justify">

**Current state:** §7.2 stage 2 says the sync module "invokes shruggie-indexer to produce IndexEntry records." §15.1 lists shruggie-indexer as a dependency that is "invoked as subprocess or library." This leaves the invocation method unresolved: is it a subprocess call to the `shruggie-indexer` CLI (requiring the binary on `PATH`), a Python library import calling `index_path()` directly (requiring `shruggie-indexer` as a pip dependency), or both with a preference order?

</div>

<div style="text-align:justify">

**What is needed:** A definitive statement on the invocation method. The shruggie-indexer spec (§9) defines a clean Python API (`index_path()`), which suggests library invocation is viable. If both methods are supported, the spec should define which is the default and under what circumstances the alternative is used (e.g., library import when available, subprocess fallback for standalone executable deployments). This decision affects dependency declarations, error handling, and the sync module's interface design.

</div>

**Previously identified:** No.

---

<a name="28-vault-get-by-id-resolution-path" id="28-vault-get-by-id-resolution-path"></a>
### 2.8. Vault get-by-id Resolution Path

**Spec sections:** §5.2, §5.4

<div style="text-align:justify">

**Current state:** §5.2 defines the `get` operation as "Retrieve bytes by `id` or `storage_name`." However, §5.4 states the invariant: "The vault module has no knowledge of catalog references, collections, or search. It stores and retrieves bytes." The vault stores objects keyed by `storage_name`. Resolving an `id` to a `storage_name` requires catalog knowledge (since `storage_name` is derived from `id` plus extension, and the extension is metadata the vault does not track independently).

</div>

<div style="text-align:justify">

**What is needed:** Clarify the `get` operation's contract. Either: (a) the vault's `get` accepts only `storage_name` and the `id`-based lookup is the caller's responsibility (the caller queries the catalog to resolve `id` to `storage_name`, then calls vault `get` with the result), or (b) the vault accepts `id` and performs a filesystem glob/prefix search (since `storage_name` starts with the `id` hash). Option (a) is cleaner and consistent with the vault's "no catalog knowledge" invariant; option (b) avoids a catalog round-trip but introduces implicit coupling. The spec should pick one and update §5.2 accordingly.

</div>

**Previously identified:** No.

<hr class="print-page-break">

<a name="3-deferred-items" id="3-deferred-items"></a>
## 3. Deferred Items

<div style="text-align:justify">

These gaps fall outside Phase 2 scope. They are documented here for tracking but do not need resolution before Sprint 1. Each will require specification work before the phase that introduces its functionality.

</div>

<a name="31-sync-plan-output-format" id="31-sync-plan-output-format"></a>
### 3.1. Sync Plan Output Format

**Phase:** 3 (Pipeline). §7.3 describes intent but defines no schema or structure for the Sync Plan output.

<a name="32-resumable-sync-state-persistence" id="32-resumable-sync-state-persistence"></a>
### 3.2. Resumable Sync State Persistence

**Phase:** 3 (Pipeline). §7.4 states sync is "restartable at any point" and "resumes from the point of interruption," but does not define how in-progress state is persisted (checkpoint file, database table, manifest).

<a name="33-reference-model-schema" id="33-reference-model-schema"></a>
### 3.3. Reference Model Schema

**Phase:** 4 (Search and Scale). §6.2 and §8 reference collections, projects, tenants, and snapshots as reference types, but no table definitions or relationship structures are specified.

<a name="34-temporal-correlation-storage-model" id="34-temporal-correlation-storage-model"></a>
### 3.4. Temporal Correlation Storage Model

**Phase:** 4 (Search and Scale). §6.2 and §6.5 describe the catalog's role in correlating IndexEntry snapshots across time, but the storage model for multiple snapshots of the same identity (and how they are queried) is not defined.

<a name="35-error-type-hierarchy" id="35-error-type-hierarchy"></a>
### 3.5. Error Type Hierarchy

<div style="text-align:justify">

**Phase:** All (but not blocking). §9 defines tolerated failure modes and recovery principles. A concrete exception hierarchy (base exception class, module-specific subclasses, expected vs. unexpected error classification) would help agents produce consistent error handling, but its absence is unlikely to cause incorrect implementations in Phase 2. This can be defined in the Sprint 1 plan itself as a foundational work item.

</div>

<hr class="print-page-break">

<a name="4-minor-issues-and-inconsistencies" id="4-minor-issues-and-inconsistencies"></a>
## 4. Minor Issues and Inconsistencies

<a name="41-license-field-contradiction" id="41-license-field-contradiction"></a>
### 4.1. License Field Contradiction

<div style="text-align:justify">

The document header table states "Apache License v2.0" and the License row links to the Apache 2.0 text. However, §10.1's description of the `LICENSE` file says "License text (license selection TBD)." These two statements contradict each other. If Apache 2.0 is the decision, the §10.1 entry should say so.

</div>

<a name="42-cli-subcommand-tree-hedging" id="42-cli-subcommand-tree-hedging"></a>
### 4.2. CLI Subcommand Tree Hedging

<div style="text-align:justify">

§12.1 introduces the CLI command structure with the qualifier "the exact subcommand tree is defined during implementation, but the following structure reflects the expected shape." This hedging is understandable for a draft, but it means an agent implementing the CLI entry point will treat the subcommand tree as non-authoritative and may deviate. If the tree shown is intended to be canonical, the hedging language should be removed. If it is genuinely provisional, the sprint plan for CLI work should lock it down.

</div>

<a name="43-changelog-copy-automation" id="43-changelog-copy-automation"></a>
### 4.3. Changelog Copy Automation

<div style="text-align:justify">

§11.3 describes the `docs/changelog.md` to `CHANGELOG.md` synchronization as manual. This is fine operationally, but the spec should clarify whether the docs CI workflow (§11.5) is expected to perform this copy as a build step, or whether it relies on the developer having manually copied the file before pushing. The current wording ("the copy is maintained manually") suggests no automation, but the strict build mode will fail if they diverge. A one-line `cp` in the workflow or a pre-build hook would close this loop, and the spec should state the intended approach.

</div>

<hr class="print-page-break">

<a name="5-items-that-are-fine" id="5-items-that-are-fine"></a>
## 5. Items That Are Fine

<div style="text-align:justify">

The following areas were reviewed and found to be sufficiently detailed for agent implementation. No changes needed.

</div>

- **IndexEntry contract (§4).** Clear ownership, schema location, evolution rules, and consumer obligations. No ambiguity.
- **Vault module (§5).** Operations, invariants, and verification modes are well-defined (except the get-by-id issue in §2.8).
- **Catalog module behavioral contracts (§6).** Operations and invariants are clear; only the underlying schema is missing.
- **Sync module pipeline stages (§7).** The six-stage pipeline is unambiguous for the stages within Phase 2 scope.
- **Reference and deletion model (§8).** Two-phase deletion is clearly specified.
- **Failure model (§9).** Tolerated failures and recovery principles are adequate.
- **Repository structure (§10).** Complete and consistent with the source package layout.
- **Documentation site (§11).** MkDocs configuration, navigation, deployment, and changelog sync are all well-specified.
- **File encoding and JSON conventions (§14).** No gaps.
- **External dependencies (§15).** Known dependencies are identified with categories and failure modes.
- **Logging (§16).** Logger naming, output destinations, and file naming pattern are sufficient.
- **Testing (§17).** Test organization by type, markers, and pytest conventions are clear.
- **Packaging and distribution (§18).** PyInstaller pipeline, version management, and release process are adequate.
- **Platform portability (§19).** Cross-platform principles and platform-specific considerations are thorough.
- **Security and safety (§20).** Path validation, destructive operation safeguards, credential handling, and resource limits are well-specified.
- **Performance considerations (§21).** Guidance on chunked I/O, batch operations, and index design is sufficient.
- **Development phases (§22).** Phase scoping and ordering are clear.
- **Development workflow (§23).** The two-layer model, handoff protocol, session report format, agent execution modes, git conventions, and review checklist are all detailed enough to follow without clarification.
- **Composition rules (§24).** Clear and concise.
- **Future considerations (§25).** Appropriately scoped.
