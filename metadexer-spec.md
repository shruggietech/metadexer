# Metadexer — Technical Specification

| **Attribute** | **Value** |
|---------------|-----------|
| Project Name | Metadexer |
| Project Slug | `metadexer` |
| Domain | [metadexer.com](https://metadexer.com) (reserved) |
| Repository | [github.com/shruggietech/metadexer](https://github.com/shruggietech/metadexer) |
| License | [Apache License v2.0](https://www.apache.org/licenses/LICENSE-2.0) |
| Version | Pre-release (0.1.0 target) |
| Author | William Thompson (ShruggieTech LLC) |
| Latest Revision Date | 2026-03-19 |
| Document Status | DRAFT |
| Audience | AI-first, Human-second |

---

## Table of Contents

- [1. Document Information](#1-document-information)
  - [1.1. Purpose and Audience](#11-purpose-and-audience)
  - [1.2. Scope](#12-scope)
  - [1.3. Document Maintenance](#13-document-maintenance)
  - [1.4. Conventions Used in This Document](#14-conventions-used-in-this-document)
  - [1.5. Terminology](#15-terminology)
  - [1.6. Reference Documents](#16-reference-documents)
- [2. Project Overview](#2-project-overview)
  - [2.1. Project Identity](#21-project-identity)
  - [2.2. Relationship to shruggie-indexer](#22-relationship-to-shruggie-indexer)
  - [2.3. Design Goals](#23-design-goals)
  - [2.4. Non-Goals](#24-non-goals)
  - [2.5. Platform and Runtime Requirements](#25-platform-and-runtime-requirements)
- [3. Architecture](#3-architecture)
  - [3.1. Component Map](#31-component-map)
  - [3.2. Module Responsibilities](#32-module-responsibilities)
  - [3.3. Data Flow](#33-data-flow)
  - [3.4. Operational Modes](#34-operational-modes)
- [4. The IndexEntry Contract](#4-the-indexentry-contract)
  - [4.1. Ownership and Authority](#41-ownership-and-authority)
  - [4.2. Schema Location](#42-schema-location)
  - [4.3. Schema Evolution Rules](#43-schema-evolution-rules)
  - [4.4. Consumer Obligations](#44-consumer-obligations)
- [5. Vault Module](#5-vault-module)
  - [5.1. Purpose](#51-purpose)
  - [5.2. Operations](#52-operations)
    - [5.2.1. File-Based Operations](#521-file-based-operations)
    - [5.2.2. Inline Operations](#522-inline-operations)
  - [5.3. Storage Backends](#53-storage-backends)
  - [5.4. Backend Interface](#54-backend-interface)
    - [5.4.1. VaultBackend Abstract Base Class](#541-vaultbackend-abstract-base-class)
    - [5.4.2. VaultStore Facade](#542-vaultstore-facade)
    - [5.4.3. Result Types](#543-result-types)
    - [5.4.4. VaultInlineStore](#544-vaultinlinestore)
  - [5.5. Invariants](#55-invariants)
  - [5.6. Verification Modes](#56-verification-modes)
- [6. Catalog Module](#6-catalog-module)
  - [6.1. Purpose](#61-purpose)
  - [6.2. Operations](#62-operations)
  - [6.3. Database Backends](#63-database-backends)
  - [6.4. Backend Interface](#64-backend-interface)
  - [6.5. Storage Routing](#65-storage-routing)
  - [6.6. Catalog-Indexer Contract](#66-catalog-indexer-contract)
  - [6.7. Invariants](#67-invariants)
  - [6.8. Catalog Database Schema](#68-catalog-database-schema)
- [7. Sync Module](#7-sync-module)
  - [7.1. Purpose](#71-purpose)
  - [7.2. Pipeline Stages](#72-pipeline-stages)
  - [7.3. Sync Plans](#73-sync-plans)
  - [7.4. Invariants](#74-invariants)
- [8. Reference and Deletion Model](#8-reference-and-deletion-model)
  - [8.1. Asset Immutability](#81-asset-immutability)
  - [8.2. Two-Phase Deletion](#82-two-phase-deletion)
- [9. Failure Model](#9-failure-model)
  - [9.1. Tolerated Failure Modes](#91-tolerated-failure-modes)
  - [9.2. Recovery Principles](#92-recovery-principles)
  - [9.3. Exception Hierarchy](#93-exception-hierarchy)
- [10. Repository Structure](#10-repository-structure)
  - [10.1. Top-Level Layout](#101-top-level-layout)
  - [10.2. Source Package Layout](#102-source-package-layout)
  - [10.3. Documentation Artifacts](#103-documentation-artifacts)
  - [10.4. Scripts and Build Tooling](#104-scripts-and-build-tooling)
- [11. Documentation Site](#11-documentation-site)
  - [11.1. Site Configuration](#111-site-configuration)
  - [11.2. Navigation Structure](#112-navigation-structure)
  - [11.3. Changelog Synchronization](#113-changelog-synchronization)
  - [11.4. Build and Preview](#114-build-and-preview)
  - [11.5. Deployment](#115-deployment)
  - [11.6. Dependencies](#116-dependencies)
- [12. CLI Interface](#12-cli-interface)
  - [12.1. Command Structure](#121-command-structure)
  - [12.2. CLI Conventions](#122-cli-conventions)
- [13. Configuration](#13-configuration)
  - [13.1. Configuration Architecture](#131-configuration-architecture)
  - [13.2. Application Data Directory](#132-application-data-directory)
  - [13.3. Configuration Keys and Defaults](#133-configuration-keys-and-defaults)
- [14. File Encoding and JSON Conventions](#14-file-encoding-and-json-conventions)
  - [14.1. File Encoding and Line Endings](#141-file-encoding-and-line-endings)
  - [14.2. JSON Conventions](#142-json-conventions)
- [15. External Dependencies](#15-external-dependencies)
  - [15.1. Python Dependencies](#151-python-dependencies)
  - [15.2. External Service Dependencies](#152-external-service-dependencies)
  - [15.3. Dependency Verification at Runtime](#153-dependency-verification-at-runtime)
- [16. Logging and Diagnostics](#16-logging-and-diagnostics)
- [17. Testing](#17-testing)
- [18. Packaging and Distribution](#18-packaging-and-distribution)
  - [18.1. pyproject.toml Configuration](#181-pyprojecttoml-configuration)
  - [18.2. Build and Release Pipeline](#182-build-and-release-pipeline)
  - [18.3. Version Management](#183-version-management)
- [19. Platform Portability](#19-platform-portability)
  - [19.1. Cross-Platform Design Principles](#191-cross-platform-design-principles)
  - [19.2. Platform-Specific Considerations](#192-platform-specific-considerations)
- [20. Security and Safety](#20-security-and-safety)
  - [20.1. Path Validation and Sanitization](#201-path-validation-and-sanitization)
  - [20.2. Destructive Operation Safeguards](#202-destructive-operation-safeguards)
  - [20.3. Credential and Secret Handling](#203-credential-and-secret-handling)
  - [20.4. Large File and Resource Limit Handling](#204-large-file-and-resource-limit-handling)
- [21. Performance Considerations](#21-performance-considerations)
  - [21.1. Ingestion Pipeline Performance](#211-ingestion-pipeline-performance)
  - [21.2. Catalog Query Performance](#212-catalog-query-performance)
  - [21.3. Vault I/O Performance](#213-vault-io-performance)
- [22. Development Phases](#22-development-phases)
  - [22.1. Phase 2: Storage and Catalog](#221-phase-2-storage-and-catalog)
  - [22.2. Phase 3: Pipeline](#222-phase-3-pipeline)
  - [22.3. Phase 4: Search and Scale](#223-phase-4-search-and-scale)
  - [22.4. Phase 5: Integration and Polish](#224-phase-5-integration-and-polish)
- [23. Development Workflow](#23-development-workflow)
  - [23.1. Purpose and Authority](#231-purpose-and-authority)
  - [23.2. Workflow Layers](#232-workflow-layers)
  - [23.3. Handoff Protocol](#233-handoff-protocol)
  - [23.4. Agent Execution Model](#234-agent-execution-model)
  - [23.5. Git Conventions](#235-git-conventions)
  - [23.6. Agent Context Management](#236-agent-context-management)
  - [23.7. Review and Integration](#237-review-and-integration)
  - [23.8. Tooling Configuration](#238-tooling-configuration)
  - [23.9. Workflow Summary](#239-workflow-summary)
- [24. Composition Rules](#24-composition-rules)
- [25. Future Considerations](#25-future-considerations)

---

## 1. Document Information

### 1.1. Purpose and Audience

This document is the authoritative technical specification for `metadexer`, a content-addressed asset management system that handles storage, cataloging, deduplication, and search across large, heterogeneous collections of digital data.

The specification is written for an **AI-first, Human-second** audience. Its primary consumers are AI implementation agents operating within isolated context windows during sprint-based development. Every section provides sufficient detail for an AI agent to produce correct design decisions without requiring interactive clarification. Human developers and maintainers are the secondary audience.

This specification describes:

- The architectural decomposition of metadexer into its three internal modules (vault, catalog, sync) and their relationship to the external `shruggie-indexer` dependency.
- The behavioral contracts, invariants, and responsibility boundaries for each module.
- The repository structure, documentation site, configuration architecture, CLI design, and operational modes.
- The platform portability, security, and performance constraints that govern all implementation work.
- The development phasing that governs implementation ordering.
- The development workflow that governs how planning, implementation, review, and integration are conducted across all development sessions.

This specification does NOT serve as a user guide, tutorial, or API reference. Those artifacts are separate deliverables.

### 1.2. Scope

#### In Scope

- **Vault module.** Content-addressed storage (file-based and inline text) with local filesystem and S3-compatible backends. Put, get, head, verify, and prune operations.
- **Catalog module.** Metadata registry and search engine. IndexEntry ingestion, field projection, basic and full-text search, full-text search indexing of vault-stored inline content, reference tracking, and temporal correlation. PostgreSQL and SQLite backends.
- **Sync module.** Ingestion pipeline orchestration. Sync Plan generation, deduplication, storage routing, resumable uploads, and idempotent catalog commits.
- **CLI interface.** The canonical user interface for all operations, built on `click`.
- **Configuration system.** Layered TOML configuration with compiled defaults, user config, project-local config, and CLI overrides.
- **Documentation site.** MkDocs-based documentation with the Material for MkDocs theme, deployed via GitHub Pages.
- **Packaging and distribution.** PyInstaller-based standalone executables distributed via GitHub Releases.
- **Development workflow.** Two-layer workflow model (admin/coding), handoff protocol, agent execution model, agent context management, and review procedures.

#### Out of Scope

- **shruggie-indexer internals.** The indexer has its own specification (`shruggie-indexer-spec.md`). metadexer consumes the IndexEntry contract; it does not define or extend it.
- **Web UI.** A browser-based interface for search and browsing is a future extension ([§25](#25-future-considerations)), not part of the core specification.
- **hotwire integration.** Automated real-time feed ingestion via the hotwire pipeline is a future extension.
- **Embedding and vector search.** Semantic retrieval via vector similarity is a future extension layered on top of the catalog.

### 1.3. Document Maintenance

This specification is maintained as a living document alongside the codebase. When the specification and the implementation disagree, the specification is presumed correct unless a deliberate amendment has been recorded in the document history.

### 1.4. Conventions Used in This Document

This specification uses the requirement level keywords defined in RFC 2119. These keywords are capitalized when used in their RFC 2119 sense:

| Keyword | Meaning |
|---------|---------|
| <span style="white-space: nowrap;">**MUST** / **MUST NOT**</span> | Absolute requirement or prohibition. |
| <span style="white-space: nowrap;">**SHALL** / **SHALL NOT**</span> | Synonymous with MUST / MUST NOT. |
| <span style="white-space: nowrap;">**SHOULD** / **SHOULD NOT**</span> | Strong recommendation. Deviation must be deliberate. |
| <span style="white-space: nowrap;">**MAY**</span> | Truly optional. |

Typographic conventions:

- `Monospace` denotes code identifiers, file paths, CLI flags, configuration keys, and literal values.
- **Bold** denotes emphasis or key terms being defined.
- *Italic* denotes document titles, variable placeholders, or first use of a defined term.
- `§N.N` denotes a cross-reference to a section within this specification.

Code examples use Python syntax unless otherwise noted. Examples are illustrative; they demonstrate intent and structure but are not necessarily the exact implementation.

### 1.5. Terminology

| Term | Definition |
|------|------------|
| <span style="white-space: nowrap;">**IndexEntry**</span> | A structured JSON record produced by shruggie-indexer that serves as the authoritative metadata description of a content object. Defined by the v2 schema. |
| <span style="white-space: nowrap;">**Content-addressed**</span> | An identity model where objects are identified by a hash of their byte content, not by filename or path. |
| <span style="white-space: nowrap;">**Vault**</span> | The metadexer module responsible for content storage (file-based and inline text) under deterministic, content-derived keys. The sole owner of stored content in the system. |
| <span style="white-space: nowrap;">**Catalog**</span> | The metadexer module responsible for metadata storage, indexing, search, and reference tracking. |
| <span style="white-space: nowrap;">**Sync**</span> | The metadexer module responsible for orchestrating the ingestion pipeline across the indexer, vault, and catalog. |
| <span style="white-space: nowrap;">**Sync Plan**</span> | A dry-run preview of pending operations generated by the sync module before committing any changes. |
| <span style="white-space: nowrap;">**Storage routing**</span> | The rule-based decision process that determines which vault storage surface receives ingested content: the file-based backend (local or S3) for large or binary content, or the inline database surface for small text-based content. |
| <span style="white-space: nowrap;">**Sidecar file**</span> | An external metadata file that lives alongside the file it describes, identified by filename pattern matching (e.g., `video.mp4` may have a sidecar `video.srt`). Sidecar discovery and parsing is handled by shruggie-indexer. |
| <span style="white-space: nowrap;">**Reference**</span> | A mutable pointer (collection, project, tenant, snapshot) that links to an immutable asset in the catalog. |
| <span style="white-space: nowrap;">**Prune**</span> | The explicit operation that removes unreferenced objects from the vault. Never triggered automatically. |
| <span style="white-space: nowrap;">**`storage_name`**</span> | The deterministic filename derived from an item's `id` and extension, produced by shruggie-indexer. Used as the vault storage key. |
| <span style="white-space: nowrap;">**Admin layer**</span> | The strategic planning tier of the development workflow. Operates in browser-based AI chat sessions. Produces specifications, sprint plans, and agent context files. Does not produce code. |
| <span style="white-space: nowrap;">**Coding layer**</span> | The implementation tier of the development workflow. Operates in IDE-based or terminal-based AI coding agent sessions. Consumes sprint plans and specifications, produces code. |
| <span style="white-space: nowrap;">**Sprint document**</span> | A structured planning artifact produced by the admin layer that defines a batch of work items for the coding layer. Filed in `.handoff/plans/`. |
| <span style="white-space: nowrap;">**Session report**</span> | A structured summary produced by (or on behalf of) the coding layer at the end of a development session. Filed in `.handoff/reports/`. |
| <span style="white-space: nowrap;">**Agent context file**</span> | A repository-root file (`CLAUDE.md`, `.github/copilot-instructions.md`) that provides persistent project-level context to AI coding agents. |

### 1.6. Reference Documents

| Document | Location | Description |
|----------|----------|-------------|
| metadexer Overview | `.archive/20260305-004-metadexer-overview.md` | High-level project overview covering vision, architecture, use cases, and development roadmap. This specification supersedes the overview for all technical details. |
| shruggie-indexer Spec | `shruggie-indexer` repository: `shruggie-indexer-spec.md` | The authoritative technical specification for the indexer. Defines the IndexEntry v2 schema, all indexing behavior, sidecar handling, and output contracts. |
| IndexEntry v2 Schema | [schemas.shruggie.tech/data/shruggie-indexer-v2.schema.json](https://schemas.shruggie.tech/data/shruggie-indexer-v2.schema.json) | The canonical JSON Schema definition for the v2 IndexEntry format. |
| Sprint Document Format | metadexer Overview, Appendix D | Defines the five-section structure for sprint planning documents: header block, purpose and context, implementation ordering, work item sections, and specification update directive. |

---

## 2. Project Overview

### 2.1. Project Identity

| Property | Value |
|----------|-------|
| <span style="white-space: nowrap;">Product name</span> | metadexer |
| <span style="white-space: nowrap;">Organization</span> | ShruggieTech LLC (https://shruggie.tech) |
| <span style="white-space: nowrap;">Author</span> | William Thompson |
| <span style="white-space: nowrap;">Language</span> | Python 3.12+ |
| <span style="white-space: nowrap;">Package name</span> | `metadexer` |
| <span style="white-space: nowrap;">CLI command</span> | `metadexer` |
| <span style="white-space: nowrap;">Domain</span> | metadexer.com (reserved) |

**metadexer** is the product name. It is what users install, what the CLI is called, what the documentation refers to, and what appears on metadexer.com.

**ShruggieTech** is the organizational identity (ShruggieTech LLC). It is the publisher of both shruggie-indexer and metadexer. It appears in license headers, copyright notices, and GitHub organization naming. It is not a product name.

### 2.2. Relationship to shruggie-indexer

shruggie-indexer is a standalone tool that predates the metadexer product identity. It has its own repository, its own release schedule, its own specification, and its own branding. It is a dependency of metadexer, not a sub-component of it.

The relationship is defined by a single contract: the **IndexEntry v2 JSON schema**. shruggie-indexer produces IndexEntry records; metadexer consumes them. metadexer MUST NOT redefine IndexEntry fields or semantics. metadexer MUST NOT recompute content identity. The indexer defines truth; metadexer preserves, records, and propagates it.

shruggie-indexer v0.1.2 is the current stable release at the time of this writing. It defines identity, extracts metadata, manages sidecars, and produces well-formed IndexEntry v2 JSON.

### 2.3. Design Goals

The following properties are preserved across all implementation decisions:

- **G1 - Determinism.** The same input always produces the same output.
- **G2 - Idempotence.** Repeating an operation produces no additional side effects.
- **G3 - Composability.** The indexer works independently; metadexer modules work as a coordinated unit.
- **G4 - Auditability.** All operations are traceable; no silent mutations or deletions.
- **G5 - Minimal hidden state.** System state is observable and recoverable from durable records.
- **G6 - Clear failure modes.** Failures surface explicitly; the system does not paper over errors.
- **G7 - Offline-first capability.** Local operation is fully functional without network access.
- **G8 - CLI-first design.** CLI contracts are the canonical interface. API and GUI layers are secondary and thin.
- **G9 - Cross-platform operation.** The application MUST run on Windows, Linux, and macOS from a single codebase.

### 2.4. Non-Goals

metadexer is explicitly not:

- A traditional Digital Asset Management system optimized for marketing workflows and approval pipelines.
- A web-first application that requires a browser for core functionality.
- A SaaS product with per-seat licensing.
- A general-purpose object storage layer (MinIO, raw S3 already do this).
- A tool that makes autonomous decisions about user data.

### 2.5. Platform and Runtime Requirements

| Requirement | Value |
|-------------|-------|
| Python version | 3.12+ (enables `tomllib`, modern type hints) |
| Target platforms | Windows (x64), Linux (x64), macOS (arm64) |
| External binary dependencies | `exiftool` (required by shruggie-indexer, not directly by metadexer) |
| Configuration format | TOML (parsed by `tomllib`) |
| JSON serializer | `orjson` preferred, `json` stdlib as silent fallback |

---

## 3. Architecture

### 3.1. Component Map

```
shruggie-indexer (standalone tool, own repository)
    │
    │  produces IndexEntry v2 JSON
    │
    ▼
metadexer (single application, single repository)
    ├── vault module    - content-addressed storage (files and inline text)
    ├── catalog module  - metadata registry, search, references
    └── sync module     - ingestion pipeline orchestration
```

The indexer is a standalone tool because it genuinely is one. It operates on local files, produces JSON output, has no dependency on metadexer, and is useful on its own. People use it independently to index files, generate metadata, and pipe the output into their own scripts.

The vault, catalog, and sync modules share the IndexEntry contract, share configuration, share a data lifecycle, and are invoked together in normal operation. They live in a single repository as internal modules of the metadexer application. Each module maintains a clean responsibility boundary (the vault module does not know about catalog references; the catalog module does not store content of any kind), but they are not separate projects.

### 3.2. Module Responsibilities

| Concern | Owner |
|---------|-------|
| Identity generation and metadata extraction | <span style="white-space: nowrap;">shruggie-indexer</span> |
| Content storage (file-based and inline text) | <span style="white-space: nowrap;">metadexer vault module</span> |
| Structured metadata, references, and search | <span style="white-space: nowrap;">metadexer catalog module</span> |
| Pipeline orchestration and storage routing | <span style="white-space: nowrap;">metadexer sync module</span> |

No module is permitted to silently absorb a neighbor's responsibility. In particular: the vault is the sole owner of stored content regardless of content type, size, or storage surface. The catalog indexes, queries, and tracks metadata but never persists file content. The sync module decides where content goes but never stores or indexes it directly.

### 3.3. Data Flow

The standard ingestion pipeline follows this sequence:

1. The sync module accepts a directory or file target as input.
2. The sync module invokes shruggie-indexer to produce IndexEntry records for each target.
3. For each IndexEntry, the sync module checks the catalog and vault for already-present assets. Duplicates are skipped.
4. Storage routing rules examine the IndexEntry. Small text-based content is routed to the vault's inline database surface. Large or binary content is routed to the vault's file-based backend.
5. Content is stored in the vault: bytes to the file backend for file-routed content, text to the inline database surface for inline-routed content.
6. The IndexEntry is committed to the catalog only after vault storage is confirmed complete. The sync module passes the stored text content (if inline-routed) to the catalog for search index construction.

### 3.4. Operational Modes

**Local mode.** Indexer, local vault, local catalog. No server required. Suitable for offline archival and single-user workflows.

**Remote mode.** The client invokes the indexer and computes identity locally. The client uploads bytes to a remote vault. The client commits metadata to a remote catalog. The server MAY verify integrity asynchronously by policy.

In both modes, identity always originates from the client. The sync module never delegates identity decisions to a server.

---

## 4. The IndexEntry Contract

### 4.1. Ownership and Authority

The IndexEntry v2 JSON schema is defined and owned by shruggie-indexer. metadexer consumes it as a fixed contract. The authoritative behavioral specification for IndexEntry fields, types, and semantics lives in the shruggie-indexer specification (`shruggie-indexer-spec.md`, §5). This document does not duplicate that content.

metadexer MUST NOT redefine IndexEntry fields or their semantics. metadexer MUST NOT add fields to, remove fields from, or structurally alter an IndexEntry record after it is produced by the indexer. An IndexEntry received by metadexer is treated as an immutable artifact.

### 4.2. Schema Location

The authoritative machine-readable schema is hosted at:

```
https://schemas.shruggie.tech/data/shruggie-indexer-v2.schema.json
```

This document uses JSON Schema Draft-07. A local copy is committed to the indexer repository at `docs/schema/shruggie-indexer-v2.schema.json`.

### 4.3. Schema Evolution Rules

These rules are owned by the shruggie-indexer specification and summarized here for metadexer implementers:

- **Additive fields are non-breaking.** New optional fields MAY be added to v2 without incrementing `schema_version`. Consumers MUST tolerate unknown optional fields.
- **Structural changes require a version bump.** Renaming, retyping, removing a required field, or altering semantic meaning constitutes a breaking change and MUST increment `schema_version`.
- **Deprecation before removal.** A field marked deprecated in version N is emitted but ignored, then removed in version N+1.
- **Consumers dispatch on `schema_version`.** The integer value `2` is checked before parsing. Documents with unrecognized versions SHOULD be rejected.

### 4.4. Consumer Obligations

metadexer, as an IndexEntry consumer, MUST:

- Validate `schema_version` before processing.
- Tolerate unknown optional fields without error.
- Reject records with unrecognized `schema_version` values.
- Never recompute identity fields (`id`, `storage_name`, `hashes`) unless performing an explicit integrity verification.
- Never rewrite or amend an IndexEntry outside of the indexer's own operation.

---

## 5. Vault Module

### 5.1. Purpose

The vault module is the sole owner of stored content in the metadexer system. It preserves content under deterministic keys derived from the IndexEntry's `storage_name` field. The vault provides two storage surfaces: a file-based backend for binary and large content (local filesystem or S3-compatible object storage), and an inline database surface for small text-based content. Both surfaces share the same identity model and `storage_name` key space. The vault is responsible for content, not metadata.

### 5.2. Operations

#### 5.2.1. File-Based Operations

| Operation | Description |
|-----------|-------------|
| <span style="white-space: nowrap;">**put**</span> | Store bytes under the `storage_name` key. Write-once: if the key already exists with identical content, the operation is a no-op. If the key exists with different content, this is a hash collision and MUST be surfaced as an error. |
| <span style="white-space: nowrap;">**get**</span> | Retrieve bytes by `storage_name`. The vault does not resolve `id` to `storage_name`; that mapping is the caller's responsibility (typically resolved via a catalog lookup). This preserves the vault's "no catalog knowledge" invariant ([§5.5](#55-invariants)). |
| <span style="white-space: nowrap;">**head**</span> | Check existence of an object without retrieving its bytes. |
| <span style="white-space: nowrap;">**verify**</span> | Re-hash stored bytes and compare against a provided IndexEntry. Verification is always explicit, never triggered automatically during ingest. |
| <span style="white-space: nowrap;">**prune**</span> | Remove unreferenced objects. Pruning is always explicit, never triggered automatically. Requires reconciliation against the catalog to determine which objects are unreferenced. |

#### 5.2.2. Inline Operations

| Operation | Description |
|-----------|-------------|
| <span style="white-space: nowrap;">**put_inline**</span> | Store text content under the `storage_name` key in the inline database surface. Write-once with the same deduplication semantics as file-based `put`: if the key already exists, the operation is a no-op. |
| <span style="white-space: nowrap;">**get_inline**</span> | Retrieve text content by `storage_name` from the inline database surface. |

Inline operations do not support `verify` (there are no hashes to compare against for text stored via this path) or `prune` (inline pruning follows the same reconciliation model as file-based pruning and is deferred to Phase 4).

### 5.3. Storage Backends

**Local filesystem.** The primary backend for local-mode operation. Objects are stored as files in a content-addressed directory structure under a configurable vault root path. The directory layout uses a two-character prefix sharding scheme derived from the first two characters of the `storage_name`:

```
<vault_root>/<prefix>/<storage_name>
```

Given a vault root of `/data/vault` and a `storage_name` of `a1b2c3d4e5f6.mp4`, the full storage path is:

```
/data/vault/a1/a1b2c3d4e5f6.mp4
```

The prefix is always the first two characters of `storage_name`, lowercased. This produces a maximum of 1,296 prefix directories (36^2, given the alphanumeric character set of `storage_name`), which prevents performance degradation from single directories with millions of entries while keeping the tree shallow enough for manual inspection. Prefix directories are created on demand during `put` operations.

**S3-compatible object storage.** For remote or hybrid deployments. Compatible with AWS S3, MinIO, MEGA S4, and any S3-compatible API. Objects are stored as keys in a configured bucket using the `storage_name` as the object key.

The local backend is the first implementation target. The S3 backend is the second.

**Inline database surface.** For small text-based content that benefits from full-text search indexing. The inline surface stores text content in a `vault_inline` table that resides in the same database instance as the catalog's `assets` table (PostgreSQL or SQLite, depending on the catalog backend selection). The vault module owns this table; the catalog module does not read from or write to it directly.

This design reflects a deliberate architectural principle: the vault is the sole owner of stored content regardless of where the bytes physically reside. Routing small text through a database table instead of writing it to the file-based backend avoids unnecessary file I/O for content whose primary value is searchability. The inline surface does not use the two-character prefix sharding scheme (it uses `storage_name` as a primary key in a flat table) and does not support chunked I/O (content is read and written atomically).

The inline database surface does not implement the `VaultBackend` ABC because its interface shape differs (text strings rather than file paths and binary streams). It is exposed through a dedicated `VaultInlineStore` class ([§5.4.4](#544-vaultinlinestore)) and integrated into the `VaultStore` facade ([§5.4.2](#542-vaultstore-facade)).

### 5.4. Backend Interface

The vault module separates I/O operations from coordination logic. File-based backend classes (`vault/backends/local.py`, `vault/backends/s3.py`) implement a common abstract interface that handles raw byte storage and retrieval. The inline store class (`vault/inline.py`) handles text content stored in a vault-owned table co-located in the catalog database. The facade class (`vault/store.py`) consumes both a file backend and an optional inline store, and adds deduplication logic, hash verification, and prune orchestration.

#### 5.4.1. VaultBackend Abstract Base Class

Defined in `vault/backends/__init__.py`. All vault backends implement this interface.

```python
from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import AbstractContextManager
from pathlib import Path
from typing import BinaryIO


class VaultBackend(ABC):
    """Abstract interface for vault storage backends."""

    @abstractmethod
    def put(self, storage_name: str, source: Path) -> None:
        """Write bytes from source file into the backend under storage_name.

        The caller (VaultStore) guarantees that storage_name does not already
        exist in this backend before calling put. Implementations MUST NOT
        perform their own existence checks. Implementations MUST validate
        that storage_name conforms to the expected key pattern (§20.1)
        before performing any I/O.
        """

    @abstractmethod
    def get(self, storage_name: str, destination: Path) -> None:
        """Copy stored bytes for storage_name to the destination path.

        Raises VaultObjectNotFoundError if storage_name does not exist.
        Implementations MUST use chunked I/O (§20.4). The chunk size is
        provided to the backend at construction time.
        """

    @abstractmethod
    def head(self, storage_name: str) -> bool:
        """Return True if storage_name exists in this backend, False otherwise."""

    @abstractmethod
    def delete(self, storage_name: str) -> None:
        """Remove the object identified by storage_name.

        Raises VaultObjectNotFoundError if storage_name does not exist.
        This method is called by VaultStore.prune for each unreferenced
        object. Backends MUST NOT perform cascade deletions or remove
        anything other than the single named object.
        """

    @abstractmethod
    def open_read(self, storage_name: str) -> AbstractContextManager[BinaryIO]:
        """Return a context manager that yields a binary readable stream.

        Usage:
            with backend.open_read("a1b2c3d4.mp4") as f:
                chunk = f.read(chunk_size)

        Used by VaultStore.verify to stream bytes through hash computation
        without writing to an intermediate file. Raises VaultObjectNotFoundError
        if storage_name does not exist.
        """

    @abstractmethod
    def iter_storage_names(self) -> Iterator[str]:
        """Yield every storage_name present in this backend.

        Used by catalog reconciliation to compare vault contents against
        catalog records. Implementations SHOULD yield names in a stable
        order (lexicographic) but callers MUST NOT depend on ordering.
        """
```

Backend constructors receive configuration values specific to their storage type. The local backend constructor accepts `root: Path` and `chunk_size: int`. The S3 backend constructor accepts `endpoint_url: str`, `bucket: str`, `prefix: str`, `region: str`, and `chunk_size: int`. All values originate from the `[vault]` and `[vault.s3]` configuration tables ([§13.3](#133-configuration-keys-and-defaults)). Credential resolution for the S3 backend follows the rules in [§20.3](#203-credential-and-secret-handling).

#### 5.4.2. VaultStore Facade

Defined in `vault/store.py`. This is the public API that the sync module, CLI, and any future consumers call. It delegates file I/O to a `VaultBackend` instance, delegates inline text storage to an optional `VaultInlineStore` instance ([§5.4.4](#544-vaultinlinestore)), and implements the module-level operations defined in [§5.2](#52-operations).

```python
from pathlib import Path


class VaultStore:
    """Vault module public API. Wraps a VaultBackend and optional VaultInlineStore."""

    def __init__(
        self,
        backend: VaultBackend,
        chunk_size: int = 8_388_608,
        inline_store: "VaultInlineStore | None" = None,
    ) -> None:
        """Initialize with a configured backend, chunk size, and optional inline store.

        The chunk_size parameter controls the buffer size used during
        streaming hash computation in verify(). It defaults to 8 MB,
        matching the vault.chunk_size_bytes configuration default.

        The inline_store parameter enables inline text storage. When None,
        put_inline() and get_inline() raise VaultError. The sync module
        is responsible for constructing the VaultInlineStore and passing
        it here based on the catalog backend selection.
        """

    def put(self, storage_name: str, source: Path) -> bool:
        """Store bytes from source under storage_name (§5.2.1, put).

        Deduplication logic:
        1. Call backend.head(storage_name).
        2. If the object already exists, return False (no-op).
        3. If the object does not exist, call backend.put(storage_name, source)
           and return True.

        Returns True if bytes were written (new object), False if the object
        already existed (deduplicated). Hash collision detection is not
        performed during put; it is deferred to explicit verify() calls.
        This is consistent with the invariant that verification is never
        triggered automatically during ingest (§5.5).
        """

    def get(self, storage_name: str, destination: Path) -> None:
        """Retrieve bytes to destination (§5.2.1, get).

        Delegates directly to backend.get(). Raises VaultObjectNotFoundError
        if the object does not exist.
        """

    def head(self, storage_name: str) -> bool:
        """Check existence without retrieving bytes (§5.2.1, head).

        Delegates directly to backend.head().
        """

    def put_inline(self, storage_name: str, content: str) -> bool:
        """Store text content under storage_name (§5.2.2, put_inline).

        Deduplication logic mirrors put(): if the key already exists,
        return False (no-op). Otherwise store and return True.

        Raises VaultError if no inline_store was provided at construction.
        """

    def get_inline(self, storage_name: str) -> str:
        """Retrieve text content by storage_name (§5.2.2, get_inline).

        Raises VaultObjectNotFoundError if the key does not exist.
        Raises VaultError if no inline_store was provided at construction.
        """

    def verify(
        self,
        storage_name: str,
        expected_hashes: dict[str, str],
    ) -> "VerifyResult":
        """Re-hash stored bytes and compare against expected hashes (§5.2.1, verify).

        Procedure:
        1. Open a streaming read via backend.open_read(storage_name).
        2. Read in chunks of chunk_size bytes.
        3. Feed each chunk into hashlib instances for every algorithm present
           in expected_hashes (at minimum md5 and sha256; sha512 if provided).
        4. Compare computed hex digests against expected_hashes values.
        5. Return a VerifyResult indicating pass/fail and per-algorithm details.

        The expected_hashes dict maps algorithm names to uppercase hex digest
        strings, matching the IndexEntry hashes field convention. Example:
        {"md5": "A1B2C3...", "sha256": "D4E5F6..."}.

        Raises VaultObjectNotFoundError if storage_name does not exist.
        Applies only to file-based storage. Inline content does not support
        verify (see §5.2.2).
        """

    def prune(
        self,
        unreferenced: set[str],
        *,
        dry_run: bool = True,
    ) -> "PruneResult":
        """Remove unreferenced objects from the vault (§5.2.1, prune).

        The unreferenced set contains storage_names that the catalog has
        determined are no longer referenced. This set is produced by the
        catalog reconciliation operation (§6.2), not by the vault itself.

        When dry_run is True (the default, per §20.2), no objects are
        deleted; the PruneResult reports what would be removed. When
        dry_run is False, backend.delete() is called for each name in
        the unreferenced set.

        Deletion failures for individual objects are recorded in the result
        but do not abort the prune operation. The operation continues with
        the remaining objects.

        Applies only to file-based storage. Inline prune is deferred to
        Phase 4 and will follow the same reconciliation model.
        """
```

#### 5.4.3. Result Types

Defined in `vault/store.py` alongside `VaultStore`. Both are frozen dataclasses.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class VerifyResult:
    """Result of a single-object vault verification."""

    storage_name: str
    passed: bool
    checked: dict[str, bool]    # algorithm name -> matched (True/False)
    expected: dict[str, str]    # algorithm name -> expected hex digest
    actual: dict[str, str]      # algorithm name -> computed hex digest


@dataclass(frozen=True)
class PruneResult:
    """Result of a vault prune operation."""

    deleted: int                     # count of objects successfully removed
    failed: int                      # count of objects where deletion failed
    dry_run: bool                    # True if no objects were actually removed
    storage_names: tuple[str, ...]   # names that were (or would be) removed
```

`VerifyResult.passed` is `True` only when every algorithm in `checked` reports `True`. If any single hash mismatches, `passed` is `False`. A hash mismatch on a previously stored object indicates either data corruption or (extremely rarely) a hash collision, and MUST be surfaced to the user as an error by the calling code.

#### 5.4.4. VaultInlineStore

Defined in `vault/inline.py`. This class manages the `vault_inline` database table, which stores small text-based content that benefits from full-text search indexing. It operates on the same database connection as the catalog backend but owns its table independently.

The separation exists to enforce the module responsibility principle from [§3.2](#32-module-responsibilities). Content storage, regardless of whether the content is a 4 GB video file or a 200-byte JSON snippet, is the vault's responsibility. The catalog knows about content (via metadata and search indexes); the vault stores content. This clean boundary ensures that future features such as multi-vault replication, P2P synchronization, or federated deployments can treat the vault as a self-contained storage unit without reasoning about content scattered across module boundaries.

```python
import sqlite3

import psycopg


class VaultInlineStore:
    """Vault inline text storage. Manages the vault_inline table.

    This class stores small text-based content in a database table
    co-located with the catalog database. The vault module owns this
    table; the catalog module does not read from or write to it.
    """

    @classmethod
    def from_sqlite(cls, connection: sqlite3.Connection) -> "VaultInlineStore":
        """Create an inline store backed by a SQLite connection.

        The connection is typically the same sqlite3.Connection used by
        the SqliteCatalogBackend. Sharing the connection ensures both
        tables live in the same database file.
        """

    @classmethod
    def from_postgres(cls, connection: psycopg.Connection) -> "VaultInlineStore":
        """Create an inline store backed by a PostgreSQL connection.

        The connection is typically the same psycopg.Connection used by
        the PostgresCatalogBackend. Sharing the connection ensures both
        tables live in the same database.
        """

    def initialize_schema(self) -> None:
        """Create the vault_inline table if it does not exist.

        Called during application startup alongside
        CatalogBackend.initialize_schema(). Idempotent.
        """

    def put(self, storage_name: str, content: str) -> bool:
        """Store text content under storage_name.

        Returns True if new, False if storage_name already exists (no-op).
        Does not update existing content on duplicate key.
        """

    def get(self, storage_name: str) -> str:
        """Retrieve text content by storage_name.

        Raises VaultObjectNotFoundError if the key does not exist.
        """

    def head(self, storage_name: str) -> bool:
        """Return True if storage_name exists in the inline store."""

    def iter_storage_names(self) -> Iterator[str]:
        """Yield every storage_name in the vault_inline table.

        Used by catalog reconciliation (Phase 4) to compare inline
        vault contents against catalog records.
        """

    def delete(self, storage_name: str) -> None:
        """Remove the entry identified by storage_name.

        Raises VaultObjectNotFoundError if the key does not exist.
        """
```

**Schema (PostgreSQL):**

```sql
CREATE TABLE vault_inline (
    storage_name    TEXT        NOT NULL,
    content         TEXT        NOT NULL,
    stored_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_vault_inline PRIMARY KEY (storage_name)
);
```

**Schema (SQLite):**

```sql
CREATE TABLE vault_inline (
    storage_name    TEXT        NOT NULL PRIMARY KEY,
    content         TEXT        NOT NULL,
    stored_at       TEXT        NOT NULL        -- ISO 8601 string
);
```

The `vault_inline` table is deliberately minimal. It stores content keyed by `storage_name` with a timestamp for auditing. No indexes beyond the primary key are needed because all queries against this table are single-key lookups. Full-text search indexing of inline content is the catalog's responsibility and uses data provided by the sync module at ingest time, not by querying this table directly.

**Connection sharing.** The `VaultInlineStore` receives an already-open database connection from the application's startup code. This connection is the same one used by the catalog backend, ensuring both tables reside in the same database file (SQLite) or schema (PostgreSQL). The vault module does not manage its own database connection lifecycle for the inline surface; it reuses the catalog's connection for co-location efficiency while maintaining logical ownership of its table.

### 5.5. Invariants

- The same `storage_name` always maps to identical content (write-once guarantee). This applies to both the file-based backend and the inline database surface.
- The vault enforces identity; it does not compute it.
- Verification is always explicit, never triggered automatically during ingest.
- Pruning is always explicit. The vault never autonomously deletes content.
- The vault module has no knowledge of catalog references, collections, or search. It stores and retrieves content.
- The vault is the sole owner of stored content. No other module persists file content or text content. The catalog stores metadata and search indexes derived from content, but not the content itself.
- Content stored in the inline database surface and content stored in the file-based backend are both vault-owned. The storage surface distinction is a performance optimization, not an ownership boundary.

### 5.6. Verification Modes

| Mode | Description |
|------|-------------|
| <span style="white-space: nowrap;">**Strict**</span> | Re-hash the entire stored object and compare against the IndexEntry. |
| <span style="white-space: nowrap;">**Sampled**</span> | Probabilistic audits across a fraction of stored objects. |
| <span style="white-space: nowrap;">**Tiered**</span> | Frequency and depth determined by policy or asset risk classification. |

Verification is invoked by policy or on-demand. It is not part of the ingest critical path. This preserves ingestion performance while maintaining the ability to audit integrity continuously.

---

## 6. Catalog Module

### 6.1. Purpose

The catalog module is the metadata registry and search engine. It records and indexes everything metadexer knows about every object. It stores IndexEntry records, projects searchable fields, tracks logical references, provides query capability, and maintains the temporal history of observed objects.

### 6.2. Operations

| Operation | Description |
|-----------|-------------|
| <span style="white-space: nowrap;">**ingest**</span> | Accept an IndexEntry record and store it. Project and index searchable fields. Duplicate ingest (same `id`) is idempotent. |
| <span style="white-space: nowrap;">**search**</span> | Query indexed fields including MIME type, size, timestamps, name, extension, and (for string-stored content) full-text search over content bodies. |
| <span style="white-space: nowrap;">**reference**</span> | Create, list, and remove logical references (collections, projects, tenants, snapshots) that point to cataloged assets. |
| <span style="white-space: nowrap;">**correlate**</span> | Link IndexEntry snapshots across time using `id`, `session_id`, and `indexed_at` to build identity evolution history. |
| <span style="white-space: nowrap;">**reconcile**</span> | Compare catalog contents against the vault to detect missing or orphaned blobs. |

### 6.3. Database Backends

**PostgreSQL** is the primary backend. It is built for power users running serious workloads: millions of objects, full-text search across years of ingested data, persistent infrastructure on a home server or dedicated machine. It is the default for anyone who takes their data seriously.

**SQLite** is a lightweight alternative for quick evaluation, portable single-file deployments, and casual use. It is fully functional but not optimized for the concurrent access patterns or query complexity that arise at scale.

### 6.4. Backend Interface

The catalog module separates database operations from business logic. Backend classes (`catalog/backends/sqlite.py`, `catalog/backends/postgres.py`) implement a common abstract interface that handles schema initialization, asset persistence, and query execution. The facade classes (`catalog/ingest.py`, `catalog/search.py`) consume a backend instance and add IndexEntry field projection, storage routing awareness, and query construction.

#### 6.4.1. CatalogBackend Abstract Base Class

Defined in `catalog/backends/__init__.py`. All catalog backends implement this interface.

```python
from abc import ABC, abstractmethod
from collections.abc import Iterator


class CatalogBackend(ABC):
    """Abstract interface for catalog database backends."""

    @abstractmethod
    def initialize_schema(self) -> None:
        """Create the assets table, indexes, triggers, and (for SQLite)
        the FTS5 virtual table if they do not already exist.

        Implementations MUST be idempotent: calling this method on a
        database that already has the schema is a no-op. The SQL
        statements use CREATE TABLE IF NOT EXISTS (and equivalents)
        to achieve this.
        """

    @abstractmethod
    def upsert_asset(self, record: "AssetRecord", search_text: str | None = None) -> bool:
        """Insert an asset record or silently skip if the id already exists.

        Returns True if a new row was inserted, False if the id already
        existed (duplicate ingest). This implements the idempotent ingest
        contract from §6.2. Implementations MUST NOT update existing rows
        on duplicate id; the original record is preserved.

        The backend is responsible for serializing record.raw_entry to the
        appropriate column type (JSONB for PostgreSQL, TEXT for SQLite)
        and converting datetime fields to the backend's native format.

        The search_text parameter, when provided, contains text content
        for full-text search index construction. The backend uses it to
        populate the search_vector column (PostgreSQL) or FTS5 index
        (SQLite) at INSERT time but does NOT store it in a dedicated
        column. The vault's inline database surface is the authoritative
        store for this content. See §5.4.4 and §6.8 for details.
        """

    @abstractmethod
    def get_by_id(self, asset_id: str) -> "AssetRecord | None":
        """Return the asset with the given id, or None if not found.

        Returns a fully populated AssetRecord with raw_entry deserialized
        to a dict.
        """

    @abstractmethod
    def get_by_storage_name(self, storage_name: str) -> "AssetRecord | None":
        """Return the asset with the given storage_name, or None if not found.

        Used by the sync module to resolve vault keys back to catalog entries.
        """

    @abstractmethod
    def search(self, query: "SearchQuery") -> "SearchResult":
        """Execute a search against the assets table.

        The backend translates the SearchQuery into native SQL. Full-text
        search uses PostgreSQL tsvector/tsquery or SQLite FTS5 as
        appropriate. Filtering, pagination, and result counting are
        handled by the backend.

        Backends MUST return SearchResult.total as the count of all
        matching rows (ignoring limit/offset) to support pagination.
        """

    @abstractmethod
    def count(self) -> int:
        """Return the total number of assets in the catalog."""

    @abstractmethod
    def iter_all_storage_names(self) -> Iterator[str]:
        """Yield every storage_name in the assets table.

        Used by catalog reconciliation (Phase 4) to compare catalog
        contents against vault contents. Implementations SHOULD use
        a server-side cursor or equivalent to avoid loading the full
        result set into memory.
        """

    @abstractmethod
    def close(self) -> None:
        """Release database connections and associated resources.

        Implementations MUST be safe to call multiple times.
        """
```

Backend constructors receive configuration values specific to their database type. The PostgreSQL backend constructor accepts `host: str`, `port: int`, `dbname: str`, and optional connection parameters. Credentials are resolved from environment variables (`PGUSER`, `PGPASSWORD`, or `METADEXER_DATABASE_URL`) per [§20.3](#203-credential-and-secret-handling). The SQLite backend constructor accepts `path: Path` for the database file location. All values originate from the `[catalog]`, `[catalog.postgres]`, and `[catalog.sqlite]` configuration tables ([§13.3](#133-configuration-keys-and-defaults)).

#### 6.4.2. Catalog Facade Classes

The catalog's public API is split across two files, reflecting the separation between write-path and read-path operations. Both classes receive the same `CatalogBackend` instance.

**CatalogIngestor** (defined in `catalog/ingest.py`):

```python
from datetime import datetime, timezone
from pathlib import Path


class CatalogIngestor:
    """Catalog write-path API. Projects IndexEntry fields and persists assets."""

    def __init__(self, backend: CatalogBackend) -> None:
        """Initialize with a configured catalog backend."""

    def ingest(
        self,
        raw_entry: dict,
        storage_mode: str,
        search_text: str | None = None,
    ) -> bool:
        """Ingest a single IndexEntry into the catalog.

        Parameters:
            raw_entry: The complete IndexEntry as a Python dict, exactly
                as produced by shruggie-indexer. This dict is stored
                verbatim in the raw_entry column.
            storage_mode: "vault" or "inline". Determined by the sync
                module's storage routing logic (§6.5), not by this method.
                Both modes indicate vault-owned storage; the distinction
                tells the catalog (and future consumers) which vault
                surface to query when retrieving content.
            search_text: Text content for full-text search index
                construction. Provided by the sync module when
                storage_mode is "inline" (the sync module reads the
                file content and passes it here for indexing). Must be
                None when storage_mode is "vault". The catalog uses
                this value to build the search_vector (PostgreSQL) or
                FTS5 index (SQLite) but does NOT persist it in the
                assets table. The vault's inline database surface is
                the authoritative store for this content.

        Procedure:
        1. Validate schema_version == 2.
        2. Project IndexEntry fields into an AssetRecord:
           - id, schema_version, type from top-level fields.
           - mime_type from top-level field (may be None).
           - extension from top-level field (may be None).
           - name_text from raw_entry["name"]["text"].
           - name_normalized from raw_entry["name"]["text"], lowercased.
           - size_bytes from raw_entry["size"]["bytes"].
           - ts_modified from raw_entry["timestamps"]["modified"]["iso"].
           - ts_created from raw_entry["timestamps"]["created"]["iso"].
           - storage_name from raw_entry["attributes"]["storage_name"].
           - storage_mode from parameter.
           - ingested_at set to datetime.now(timezone.utc).
           - raw_entry stored as the original dict.
        3. Call backend.upsert_asset(record, search_text).
        4. Return True if new, False if duplicate.

        Raises CatalogIngestError if schema_version is not 2 or if
        required fields are missing from raw_entry.
        """

    def ingest_batch(
        self,
        entries: list[tuple[dict, str, str | None]],
    ) -> "IngestResult":
        """Ingest multiple IndexEntries in a single operation.

        Each tuple contains (raw_entry, storage_mode, search_text).
        Calls self.ingest() for each entry. Individual failures are
        recorded but do not abort the batch.

        Returns an IngestResult summarizing the operation.
        """
```

**CatalogSearcher** (defined in `catalog/search.py`):

```python
class CatalogSearcher:
    """Catalog read-path API. Builds queries and returns structured results."""

    def __init__(self, backend: CatalogBackend) -> None:
        """Initialize with a configured catalog backend."""

    def search(self, query: "SearchQuery") -> "SearchResult":
        """Execute a search query against the catalog.

        Delegates to backend.search() after validating the query.
        Returns a SearchResult containing matching AssetRecords and
        a total count for pagination.
        """

    def get(self, asset_id: str) -> "AssetRecord | None":
        """Retrieve a single asset by its content-addressed id.

        Delegates to backend.get_by_id(). Returns None if not found.
        """

    def get_by_storage_name(self, storage_name: str) -> "AssetRecord | None":
        """Retrieve a single asset by its vault storage key.

        Delegates to backend.get_by_storage_name(). Returns None if
        not found.
        """

    def count(self) -> int:
        """Return the total number of assets in the catalog.

        Delegates to backend.count().
        """
```

#### 6.4.3. Shared Types

Defined in `catalog/__init__.py`. These types are the catalog module's public contract, consumed by the sync module, CLI, and any future callers.

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class AssetRecord:
    """A single asset as represented in the catalog.

    Used on both the write path (CatalogIngestor builds one from an
    IndexEntry) and the read path (CatalogBackend returns them from
    queries). Field names correspond to the assets table columns
    defined in §6.8.
    """

    id: str
    schema_version: int
    type: str                        # "file" or "directory"
    mime_type: str | None
    extension: str | None
    name_text: str | None
    name_normalized: str | None
    size_bytes: int | None
    ts_modified: datetime | None
    ts_created: datetime | None
    storage_name: str
    storage_mode: str                # "vault" or "inline"
    raw_entry: dict                  # complete IndexEntry, deserialized
    ingested_at: datetime


@dataclass(frozen=True)
class SearchQuery:
    """Parameters for a catalog search operation.

    All filter fields are optional. When None, the filter is not applied.
    Multiple filters combine with AND logic. An empty SearchQuery (all
    fields None/default) matches all assets.
    """

    text_query: str | None = None          # full-text search string (FTS)
    mime_type: str | None = None           # exact match (e.g., "image/jpeg")
    mime_prefix: str | None = None         # prefix match (e.g., "text/")
    extension: str | None = None           # exact match, no leading dot
    type: str | None = None                # "file" or "directory"
    size_min: int | None = None            # inclusive lower bound on size_bytes
    size_max: int | None = None            # inclusive upper bound on size_bytes
    modified_after: datetime | None = None  # exclusive lower bound on ts_modified
    modified_before: datetime | None = None # exclusive upper bound on ts_modified
    name_contains: str | None = None       # case-insensitive substring on name_text
    limit: int = 100                       # max results to return
    offset: int = 0                        # pagination offset


@dataclass(frozen=True)
class SearchResult:
    """Result of a catalog search operation."""

    items: tuple[AssetRecord, ...]   # matching assets for this page
    total: int                       # total matches (ignoring limit/offset)
    query: SearchQuery               # the query that produced this result


@dataclass(frozen=True)
class IngestResult:
    """Result of a batch ingest operation."""

    new: int           # count of newly inserted assets
    duplicate: int     # count of assets skipped (already existed)
    failed: int        # count of assets that failed validation
    errors: tuple[tuple[str, str], ...]  # (asset_id_or_index, error_message)
```

`AssetRecord.raw_entry` is always a Python `dict` at the interface level. Backend implementations handle serialization to JSONB (PostgreSQL) or TEXT (SQLite) on write, and deserialization back to `dict` on read. Callers never interact with the serialized form.

`SearchQuery.text_query` is passed to the database engine's native full-text search facility. For PostgreSQL, the backend converts it to a `tsquery` using `plainto_tsquery('simple', ...)`. For SQLite, the backend passes it to the FTS5 `MATCH` operator. The query string syntax is deliberately kept simple (space-separated terms with implicit AND) to avoid exposing backend-specific query languages to callers.

### 6.5. Storage Routing

Storage routing determines which vault surface receives ingested content. All content is vault-owned regardless of the routing decision; the distinction is between the vault's file-based backend (local or S3) and the vault's inline database surface ([§5.4.4](#544-vaultinlinestore)).

Storage routing is determined by configurable rulesets and by explicit user direction at ingestion time. The default ruleset applies the following rules in order:

1. **MIME type eligibility.** Only MIME types in the `text/*` family (e.g., `text/plain`, `text/html`, `text/csv`, `text/xml`) and `application/json` are eligible for inline storage. All other MIME types are routed to the file-based backend regardless of size.
2. **Size threshold.** Eligible content whose `size.bytes` is less than or equal to `65536` (64 KB) is stored via the inline database surface. Eligible content exceeding this threshold is routed to the file-based backend.
3. **Explicit override.** A CLI flag (`--force-vault` or `--force-inline`) overrides the ruleset for a given ingestion run. `--force-vault` routes all content to the file-based backend. `--force-inline` routes all eligible MIME types to the inline database surface regardless of size (binary types are never eligible for inline storage regardless of this flag).

These defaults are configurable via the `[storage_routing]` section of the configuration TOML ([§13](#13-configuration)). The configuration keys are `inline_mime_prefixes` (list of MIME type prefixes eligible for inline storage), `inline_max_bytes` (integer size threshold), and `inline_extra_types` (list of additional full MIME types eligible beyond the prefix list).

The routing decision is made by the sync module (the orchestrator) and communicated to both the vault and catalog. The `storage_mode` value recorded in the catalog's `assets` table (`"vault"` or `"inline"`) tells future consumers which vault surface to query when retrieving content for a given asset.

### 6.6. Catalog-Indexer Contract

The IndexEntry is a point-in-time snapshot. Its fields describe a file's identity, metadata, and filesystem state at the moment of indexing. Over time, content hashes change when content is modified, timestamps shift through normal filesystem operations, metadata evolves as external tools and source files change, and relative paths change when files are moved or index roots differ between runs.

This transient nature is correct by design. The indexer produces accurate snapshots. The catalog receives them, correlates them across time, and maintains a durable record of identity evolution.

### 6.7. Invariants

- `id` is globally unique per content object. Duplicate ingest is idempotent.
- Multiple references MAY point to a single asset. Assets do not belong to references.
- Reference deletion removes the reference, not the underlying asset.
- Physical deletion from the vault requires a separate, explicit prune operation.
- The catalog does not store content. All content (binary bytes and inline text) is vault-owned. The catalog stores metadata, search indexes, and pointers to vault-stored content.

### 6.8. Catalog Database Schema

This section defines the Phase 2 catalog schema. The schema covers the primary assets table required for IndexEntry ingestion, field projection, and basic search. Reference tracking tables (collections, projects, tenants, snapshots) are deferred to Phase 4 and will be specified before that phase begins.

#### 6.8.1. PostgreSQL Schema

```sql
CREATE TABLE assets (
    -- Identity (unique, content-addressed)
    id              TEXT        NOT NULL,

    -- Projected IndexEntry fields (searchable columns)
    schema_version  INTEGER     NOT NULL,
    type            TEXT        NOT NULL,       -- "file" or "directory"
    mime_type       TEXT,                       -- e.g., "image/jpeg", "text/plain"
    extension       TEXT,                       -- lowercase, no leading dot
    name_text       TEXT,                       -- IndexEntry name.text
    name_normalized TEXT,                       -- IndexEntry name.normalized
    size_bytes      BIGINT,                     -- IndexEntry size.bytes
    ts_modified     TIMESTAMPTZ,                -- IndexEntry timestamps.modified.value
    ts_created      TIMESTAMPTZ,                -- IndexEntry timestamps.created.value
    storage_name    TEXT        NOT NULL,       -- Vault storage key
    storage_mode    TEXT        NOT NULL        -- "vault" or "inline"
                    CHECK (storage_mode IN ('vault', 'inline')),

    -- Raw IndexEntry preservation
    raw_entry       JSONB       NOT NULL,       -- Complete IndexEntry JSON, immutable

    -- Full-text search (PostgreSQL native)
    search_vector   TSVECTOR,                   -- Computed at INSERT time by the backend

    -- Bookkeeping
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT pk_assets PRIMARY KEY (id),
    CONSTRAINT uq_assets_storage_name UNIQUE (storage_name)
);

-- Indexes for common query patterns (§21.2)
CREATE INDEX idx_assets_mime_type   ON assets (mime_type);
CREATE INDEX idx_assets_extension   ON assets (extension);
CREATE INDEX idx_assets_size_bytes  ON assets (size_bytes);
CREATE INDEX idx_assets_ts_modified ON assets (ts_modified);
CREATE INDEX idx_assets_name_text   ON assets USING gin (to_tsvector('simple', name_text));
CREATE INDEX idx_assets_search      ON assets USING gin (search_vector);
```

The `search_vector` column is computed application-side by the PostgreSQL catalog backend during the INSERT statement. The backend constructs the tsvector by concatenating two weighted components using the `'simple'` text search configuration: `name_text` at weight A (highest relevance) and, when the `search_text` parameter is provided by the CatalogIngestor, the inline text content at weight B. The INSERT statement uses an expression of the form:

```sql
INSERT INTO assets (..., search_vector, ...)
VALUES (...,
    setweight(to_tsvector('simple', COALESCE(%(name_text)s, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(%(search_text)s, '')), 'B'),
...);
```

This approach computes the search vector exactly once at ingest time without requiring a trigger. Since asset records are immutable (INSERT OR IGNORE, no UPDATE path in Phase 2), trigger-based maintenance is unnecessary. The text content used for weight B originates from the sync module, which reads the file and passes it to the CatalogIngestor as `search_text`. The catalog does not persist this text; it only uses it for index construction. The authoritative copy of inline text content resides in the vault's `vault_inline` table ([§5.4.4](#544-vaultinlinestore)).

#### 6.8.2. SQLite Schema

```sql
CREATE TABLE assets (
    -- Identity (unique, content-addressed)
    id              TEXT        NOT NULL PRIMARY KEY,

    -- Projected IndexEntry fields (searchable columns)
    schema_version  INTEGER     NOT NULL,
    type            TEXT        NOT NULL,
    mime_type       TEXT,
    extension       TEXT,
    name_text       TEXT,
    name_normalized TEXT,
    size_bytes      INTEGER,
    ts_modified     TEXT,       -- ISO 8601 string (SQLite has no native timestamp type)
    ts_created      TEXT,       -- ISO 8601 string
    storage_name    TEXT        NOT NULL UNIQUE,
    storage_mode    TEXT        NOT NULL CHECK (storage_mode IN ('vault', 'inline')),

    -- Raw IndexEntry preservation
    raw_entry       TEXT        NOT NULL,       -- Complete IndexEntry JSON string

    -- Bookkeeping
    ingested_at     TEXT        NOT NULL        -- ISO 8601 string
);

-- Indexes for common query patterns (§21.2)
CREATE INDEX idx_assets_mime_type   ON assets (mime_type);
CREATE INDEX idx_assets_extension   ON assets (extension);
CREATE INDEX idx_assets_size_bytes  ON assets (size_bytes);
CREATE INDEX idx_assets_ts_modified ON assets (ts_modified);

-- Full-text search via FTS5 virtual table (standalone mode)
CREATE VIRTUAL TABLE assets_fts USING fts5(
    id UNINDEXED,
    name_text,
    search_text
);
```

The SQLite FTS5 virtual table is configured in standalone mode (no `content=` directive), meaning FTS5 maintains its own internal copy of indexed text. This is the correct mode because the `search_text` column in the FTS5 table contains text content that is not stored in any column of the `assets` table (it originates from the vault's inline database surface and is passed through by the sync module at ingest time).

The SQLite catalog backend populates the FTS5 table with an explicit INSERT immediately after inserting into the `assets` table:

```sql
INSERT INTO assets_fts(id, name_text, search_text)
VALUES (?, ?, ?);
```

The `search_text` value is the inline text content provided by the CatalogIngestor's `search_text` parameter, or an empty string when `storage_mode` is `"vault"`. Synchronization triggers are not needed because asset records are immutable in Phase 2 (no UPDATE path). If Phase 4 introduces mutable fields, trigger-based FTS5 synchronization will be added at that time.

#### 6.8.3. Schema Notes

The `raw_entry` column stores the complete, unmodified IndexEntry JSON as received from the indexer. This column is the source of truth for any field not projected into a dedicated column. Projected columns exist solely for query performance; they are derived from `raw_entry` at ingest time and MUST NOT be modified independently.

The `storage_mode` column records whether content was routed to the vault's file-based backend (`"vault"`) or inline database surface (`"inline"`). Both modes represent vault-owned storage. When a consumer needs to retrieve content for an asset, it reads `storage_mode` to determine which vault surface to query: `VaultStore.get()` for file-based content, `VaultStore.get_inline()` for inline text content. The catalog never retrieves or serves content directly.

The `search_vector` column (PostgreSQL) and the `assets_fts` table (SQLite) contain search index data derived from two sources: `name_text` (always available, weight A) and inline text content (available for inline-routed assets, weight B). The inline text content used for index construction is provided by the sync module at ingest time and is not persisted in the catalog. The authoritative copy resides in the vault's `vault_inline` table ([§5.4.4](#544-vaultinlinestore)).

The schema uses `TEXT` for the `id` column rather than a binary type because `id` values are hex-encoded hash strings in the IndexEntry contract and are frequently displayed, logged, and used in CLI output. Storing them as text avoids encode/decode overhead on every read path.

---

## 7. Sync Module

### 7.1. Purpose

The sync module is the ingestion pipeline orchestrator. It connects the indexer, vault, and catalog into a reliable, resumable workflow. It is the primary interface through which data enters the metadexer system.

### 7.2. Pipeline Stages

1. Accept directory or file targets as input.
2. Invoke shruggie-indexer to produce IndexEntry records for each target.
3. Check the catalog and vault for already-present assets to avoid redundant work.
4. Apply storage routing rules to determine destination: the vault's file-based backend or its inline database surface ([§6.5](#65-storage-routing)).
5. Store content in the vault. For file-routed content, upload bytes to the file backend. For inline-routed content, write text to the inline database surface and read the content for search indexing.
6. Commit IndexEntry records to the catalog only after vault storage is confirmed complete. Pass the inline text content (if applicable) to the catalog for search index construction.

The sync module supports dry-run mode, in which it executes stages 1 through 4 and produces a Sync Plan ([§7.3](#73-sync-plans)) without committing any changes.

### 7.3. Sync Plans

A Sync Plan is a dry-run preview of pending operations. It is generated before any data is written and describes exactly what the sync module intends to do: which objects are new, which are duplicates that will be skipped, which will be routed to the vault's file-based backend, and which will be routed to the vault's inline database surface. The Sync Plan is the user's opportunity to review and approve before committing.

### 7.4. Invariants

- Identity always originates from the client. Sync never delegates identity decisions to a server.
- Upload is confirmed complete before catalog commit.
- Catalog commit is idempotent. Resubmitting the same IndexEntry is safe.
- Sync is restartable at any point without risk of corruption or data loss.
- No asset is silently overwritten or deleted.
- Resumable operation across interrupted runs. An interrupted sync resumes from the point of interruption, not from the beginning.

---

## 8. Reference and Deletion Model

### 8.1. Asset Immutability

Assets are **immutable**. Once bytes are stored in the vault and an IndexEntry is committed to the catalog, the content object is fixed. References are **mutable**. Collections, projects, tenants, and snapshots are pointers that can be created, updated, and removed without affecting the underlying asset.

### 8.2. Two-Phase Deletion

Deletion is always two-phase:

1. Remove references in the catalog.
2. Explicitly invoke vault prune to remove unreferenced objects.

This model prevents accidental data loss. No content is ever removed in a single implicit operation. Both phases require explicit user action.

---

## 9. Failure Model

### 9.1. Tolerated Failure Modes

metadexer MUST tolerate and recover from:

- Interrupted or partial uploads.
- Duplicate catalog commits.
- Partial batch failures (some objects in a batch succeed, others fail).
- Network failures at any stage of remote-mode operation.
- Temporary unavailability of either the catalog database or vault storage.

### 9.2. Recovery Principles

- **Consistency over convenience.** Incomplete operations leave the system in a known, recoverable state.
- **Explicit reconciliation over implicit repair.** The system surfaces discrepancies and requires deliberate action to resolve them.

### 9.3. Exception Hierarchy

All metadexer exceptions inherit from a common base class. The hierarchy is defined in `src/metadexer/exceptions.py` and re-exported from `src/metadexer/__init__.py` so that callers can import directly from `metadexer` or from `metadexer.exceptions`.

```python
class MetadexerError(Exception):
    """Base class for all metadexer exceptions."""


class ConfigurationError(MetadexerError):
    """Configuration is invalid or incomplete.

    Raised when:
    - A TOML configuration file contains syntax errors.
    - A required configuration value is missing (e.g., vault.root not set
      when the local backend is selected).
    - A configuration value has the wrong type or fails validation.
    - An environment variable required for credential resolution is not set
      when the corresponding backend is in use.
    """


# ── Vault exceptions ───────────────────────────────────────────────────────


class VaultError(MetadexerError):
    """Base class for vault module exceptions."""


class VaultObjectNotFoundError(VaultError):
    """A storage_name does not exist in the vault backend.

    Raised by VaultBackend.get, VaultBackend.delete, and
    VaultBackend.open_read when the requested object is absent.
    Propagated by VaultStore.get, VaultStore.verify, and
    VaultStore.prune (for individual deletion failures).
    """


class VaultHashCollisionError(VaultError):
    """A storage_name already exists with different content.

    This indicates that two distinct byte sequences produced the same
    content-derived storage_name. This is a hash collision and represents
    a data integrity violation. This exception is raised during explicit
    verification (VaultStore.verify), not during put (which uses
    head-then-write deduplication without content comparison).
    """


class VaultIOError(VaultError):
    """An I/O operation on the vault backend failed.

    Raised when the underlying storage system reports an error: file
    permission denied, disk full, S3 transport error, network timeout,
    or any other backend-specific I/O failure that is not a missing
    object (which is VaultObjectNotFoundError). The original exception
    is chained as the __cause__ for diagnostic purposes.
    """


# ── Catalog exceptions ─────────────────────────────────────────────────────


class CatalogError(MetadexerError):
    """Base class for catalog module exceptions."""


class CatalogIngestError(CatalogError):
    """An IndexEntry failed validation during catalog ingestion.

    Raised when:
    - schema_version is not 2.
    - A required IndexEntry field is missing or has the wrong type.
    - An IndexEntry cannot be projected into an AssetRecord due to
      structural issues in the raw entry dict.

    The error message includes the asset id (if available) and a
    description of the validation failure.
    """


class CatalogConnectionError(CatalogError):
    """The catalog database is unreachable or authentication failed.

    Raised by backend constructors or on first query when the database
    connection cannot be established. For PostgreSQL: connection refused,
    authentication failure, database does not exist. For SQLite: database
    file path is not writable, file is locked by another process.
    The original driver exception is chained as __cause__.
    """


class CatalogSchemaError(CatalogError):
    """Schema initialization or validation failed.

    Raised by CatalogBackend.initialize_schema when the CREATE TABLE
    or CREATE INDEX statements fail, or when an existing schema is
    detected that is incompatible with the expected structure.
    """


# ── Sync exceptions ────────────────────────────────────────────────────────


class SyncError(MetadexerError):
    """Base class for sync module exceptions."""


class IndexerInvocationError(SyncError):
    """shruggie-indexer invocation failed.

    Raised when the sync module cannot obtain IndexEntry records from
    the indexer. For library-mode invocation: the index_path() call
    raised an exception. For subprocess-mode invocation: the process
    returned a non-zero exit code or produced unparseable output. The
    original exception or process stderr is chained or included in
    the message.
    """


class SyncPipelineError(SyncError):
    """An unrecoverable error occurred during pipeline execution.

    Raised for pipeline-level failures that are not attributable to a
    single component: for example, the vault is unreachable AND the
    catalog is unreachable simultaneously, or a batch operation fails
    in a way that leaves the pipeline in an unrecoverable state. This
    is distinct from per-item failures (which are recorded in results
    and do not raise exceptions) and from component-specific errors
    (which use VaultError or CatalogError subtypes).
    """
```

#### 9.3.1. CLI Exit Code Mapping

The CLI translates exception types to exit codes. This mapping ensures that scripts and CI pipelines can distinguish between failure categories programmatically.

| Exit code | Exception type | Meaning |
|-----------|---------------|---------|
| 0 | (none) | Success. |
| 1 | Unhandled exception | Unexpected error (bug). |
| 2 | `ConfigurationError` | Invalid or incomplete configuration. |
| 3 | `VaultError` (any subtype) | Vault operation failed. |
| 4 | `CatalogError` (any subtype) | Catalog operation failed. |
| 5 | `SyncError` (any subtype) | Sync pipeline or indexer invocation failed. |

The CLI's top-level exception handler catches `MetadexerError` subtypes, logs the error message to `stderr`, and exits with the corresponding code. Unhandled exceptions (exit code 1) include a traceback in debug log output but display only a user-friendly message at the default log level.

#### 9.3.2. Exception Chaining Convention

When a metadexer exception wraps an underlying cause (a database driver error, an OS error, an indexer exception), the original exception MUST be chained using Python's `raise ... from ...` syntax. This preserves the full diagnostic chain for debugging while allowing callers to catch the metadexer-level exception type without knowing the underlying driver.

```python
# Correct: chain the original cause
try:
    connection = psycopg.connect(dsn)
except psycopg.OperationalError as e:
    raise CatalogConnectionError(f"cannot connect to PostgreSQL: {e}") from e

# Incorrect: swallow the cause
except psycopg.OperationalError as e:
    raise CatalogConnectionError(f"cannot connect to PostgreSQL: {e}")
```

---

## 10. Repository Structure

### 10.1. Top-Level Layout

```
metadexer/
├── .archive/
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
├── .handoff/
│   ├── plans/
│   └── reports/
├── docs/
├── scripts/
├── src/metadexer/
├── tests/
├── .gitignore
├── .python-version
├── CHANGELOG.md
├── CLAUDE.md
├── LICENSE
├── mkdocs.yml
├── pyproject.toml
├── README.md
└── metadexer-spec.md
```

| Path | Type | Description |
|------|------|-------------|
| <span style="white-space: nowrap;">`.archive/`</span> | Directory | Historical storage for completed, superseded, or retired project documents. Not part of the active handoff flow. Documents that were once active in `.handoff/plans/` MAY be moved here after their associated sprint is complete and integrated. Files follow the standard ShruggieTech naming convention: `<YYYYmmdd>-<ZZZ>-<title>.<ext>`, where `ZZZ` is a three-digit zero-padded increment that resets to `001` on each new date. |
| <span style="white-space: nowrap;">`.github/`</span> | Directory | GitHub-specific repository configuration. Contains `copilot-instructions.md` (project-level AI coding guidelines for GitHub Copilot) and `workflows/` with CI/CD pipeline definitions: `release.yml` for the release build pipeline ([§18](#18-packaging-and-distribution)) and `docs.yml` for automated documentation site deployment to GitHub Pages ([§11](#11-documentation-site)). |
| <span style="white-space: nowrap;">`.handoff/`</span> | Directory | Bidirectional handoff location for artifacts exchanged between the admin layer and coding layer. See [§23.3](#233-handoff-protocol) for the full handoff protocol. |
| <span style="white-space: nowrap;">`.handoff/plans/`</span> | Directory | Admin-to-coding handoff. Contains sprint planning documents and any other artifacts the admin layer produces for consumption by the coding layer. Files follow the same date-scoped naming convention as `.archive/`. |
| <span style="white-space: nowrap;">`.handoff/reports/`</span> | Directory | Coding-to-admin handoff. Contains session reports, test result summaries, and other artifacts produced by (or on behalf of) the coding layer for consumption by the admin layer. See [§23.3.4](#2334-session-report-format) for the required report format. |
| <span style="white-space: nowrap;">`docs/`</span> | Directory | All project documentation for the MkDocs-based documentation site. See [§10.3](#103-documentation-artifacts). |
| <span style="white-space: nowrap;">`scripts/`</span> | Directory | Platform-paired shell scripts for development environment setup and build automation. See [§10.4](#104-scripts-and-build-tooling). |
| <span style="white-space: nowrap;">`src/metadexer/`</span> | Directory | The Python source package. All importable code lives here. See [§10.2](#102-source-package-layout). |
| <span style="white-space: nowrap;">`tests/`</span> | Directory | All test code. Organized by test type, not by source module. See [§17](#17-testing). |
| <span style="white-space: nowrap;">`.gitignore`</span> | File | Standard Python `.gitignore` covering `__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `build/`, `*.egg-info/`, `site/`, IDE/editor files, and OS artifacts. |
| <span style="white-space: nowrap;">`.python-version`</span> | File | Contains the string `3.12` (no minor patch). Used by `pyenv` and similar version managers to auto-select the correct interpreter. |
| <span style="white-space: nowrap;">`CHANGELOG.md`</span> | File | Project changelog following [Keep a Changelog](https://keepachangelog.com/) format. Documents all notable changes organized by release version. |
| <span style="white-space: nowrap;">`CLAUDE.md`</span> | File | Project-level agent context file for Claude Code. Read automatically by Claude Code at session start. See [§23.6.1](#2361-agent-context-files) for required contents. |
| <span style="white-space: nowrap;">`LICENSE`</span> | File | Full Apache 2.0 license text, obtained from [https://www.apache.org/licenses/LICENSE-2.0.txt](https://www.apache.org/licenses/LICENSE-2.0.txt). |
| <span style="white-space: nowrap;">`mkdocs.yml`</span> | File | MkDocs configuration for the documentation site. See [§11](#11-documentation-site). |
| <span style="white-space: nowrap;">`pyproject.toml`</span> | File | Centralized project metadata, build system configuration, dependency declarations, entry points, and tool settings (`ruff`, `pytest`). |
| <span style="white-space: nowrap;">`README.md`</span> | File | Project overview, installation instructions, quick-start usage examples, and links to full documentation. |
| <span style="white-space: nowrap;">`metadexer-spec.md`</span> | File | This technical specification. Lives at the repository root for top-level visibility. |

### 10.2. Source Package Layout

```
src/metadexer/
├── __init__.py
├── _version.py
├── cli.py
├── exceptions.py             # exception hierarchy (§9.3)
├── config.py                 # configuration loading and dataclasses (§13)
├── vault/
│   ├── __init__.py
│   ├── store.py              # core put/get/head/verify logic
│   ├── inline.py             # inline database surface (§5.4.4)
│   └── backends/
│       ├── local.py          # local filesystem backend
│       └── s3.py             # S3-compatible backend
├── catalog/
│   ├── __init__.py
│   ├── ingest.py             # IndexEntry ingestion
│   ├── search.py             # query interface
│   └── backends/
│       ├── sqlite.py
│       └── postgres.py
└── sync/
    ├── __init__.py
    ├── pipeline.py           # orchestration logic
    └── plan.py               # Sync Plan generation
```

### 10.3. Documentation Artifacts

```
docs/
├── index.md
├── changelog.md
├── assets/
│   └── images/
├── getting-started/
│   ├── installation.md
│   └── quickstart.md
└── user-guide/
    ├── index.md
    ├── cli-reference.md
    ├── configuration.md
    └── platform-notes.md
```

| Path | Purpose |
|------|---------|
| <span style="white-space: nowrap;">`index.md`</span> | Documentation site landing page. Provides a project overview, quick-links section, and navigational entry points. Rendered as the site home page by MkDocs. |
| <span style="white-space: nowrap;">`changelog.md`</span> | Auto-copied from `CHANGELOG.md` at the repository root. Contains a header comment identifying it as a generated file. See [§11.3](#113-changelog-synchronization). |
| <span style="white-space: nowrap;">`assets/images/`</span> | Static image assets used by the documentation site (social previews, screenshots). |
| <span style="white-space: nowrap;">`getting-started/`</span> | Onboarding documentation: installation guide and quick-start tutorial. |
| <span style="white-space: nowrap;">`user-guide/`</span> | End-user documentation: CLI reference, configuration reference, and platform notes. Pages are populated incrementally as features stabilize. |

This layout is intentionally minimal at the DRAFT stage. Additional sections (e.g., schema reference, API documentation) are added as the corresponding features are implemented.

### 10.4. Scripts and Build Tooling

```
scripts/
├── venv-setup.sh             # Linux/macOS: create venv, install deps
├── venv-setup.ps1            # Windows: create venv, install deps
└── build.sh                  # PyInstaller build script (CI and local)
```

| Script | Purpose |
|--------|---------|
| `venv-setup.sh` / `venv-setup.ps1` | Create a Python virtual environment and install development dependencies from `pyproject.toml`. These scripts are the documented entry point for new developer setup. |
| `build.sh` | Invokes PyInstaller to produce standalone executables. Used by the GitHub Actions release pipeline and available for local builds. |

Scripts MUST be idempotent: running them multiple times produces the same result without error.

---

## 11. Documentation Site

The project documentation is published as a static site built with [MkDocs](https://www.mkdocs.org/) using the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. This matches the toolchain established by shruggie-indexer.

### 11.1. Site Configuration

The site is configured by `mkdocs.yml` at the repository root. Key configuration settings:

| Setting | Value | Purpose |
|---------|-------|---------|
| <span style="white-space: nowrap;">`site_name`</span> | `metadexer` | Displayed in the site header and browser title. |
| <span style="white-space: nowrap;">`site_description`</span> | Project tagline for SEO and social metadata. | |
| <span style="white-space: nowrap;">`site_url`</span> | The GitHub Pages URL for the project. | Base URL for canonical links and sitemap generation. |
| <span style="white-space: nowrap;">`docs_dir`</span> | `docs` | MkDocs reads all documentation source from the `docs/` directory. |
| <span style="white-space: nowrap;">`theme.name`</span> | `material` | Activates the Material for MkDocs theme. |
| <span style="white-space: nowrap;">`theme.palette.scheme`</span> | `slate` | Dark mode enabled by default. |
| <span style="white-space: nowrap;">`theme.features`</span> | Navigation tabs, instant loading, search highlighting, content tabs. | Provides a polished, responsive documentation experience. |

Required Markdown extensions: `admonition`, `pymdownx.details`, `pymdownx.superfences`.

The `nav` key in `mkdocs.yml` defines the sidebar navigation structure explicitly rather than relying on directory auto-discovery. This ensures predictable ordering and human-readable section labels.

### 11.2. Navigation Structure

```yaml
nav:
  - Home: index.md
  - Getting Started:
      - Installation: getting-started/installation.md
      - Quick Start: getting-started/quickstart.md
  - User Guide:
      - Overview: user-guide/index.md
      - CLI Reference: user-guide/cli-reference.md
      - Configuration: user-guide/configuration.md
      - Platform Notes: user-guide/platform-notes.md
  - Changelog: changelog.md
```

This navigation structure is intentionally minimal at the DRAFT stage. Additional sections are added as features are implemented.

### 11.3. Changelog Synchronization

The documentation site's changelog page (`docs/changelog.md`) is a copy of `CHANGELOG.md` at the repository root. The canonical changelog is `CHANGELOG.md` at the repository root. All edits are made there. The file begins with a header comment identifying it as auto-copied:

```markdown
<!-- THIS FILE IS AUTO-COPIED FROM CHANGELOG.md AT THE REPOSITORY ROOT. -->
<!-- DO NOT EDIT THIS FILE DIRECTLY. Edit CHANGELOG.md instead. -->
```

The docs CI workflow (`.github/workflows/docs.yml`) MUST execute `cp CHANGELOG.md docs/changelog.md` as a build step before invoking `mkdocs build`. This ensures the published site always reflects the current root changelog without requiring developers to remember a manual copy step. Local `mkdocs serve` usage assumes the developer has run this copy; the `venv-setup` scripts MAY include the copy as a convenience step.

### 11.4. Build and Preview

| Command | Purpose |
|---------|---------|
| <span style="white-space: nowrap;">`mkdocs serve`</span> | Starts a local development server with live reload at `http://127.0.0.1:8000/`. |
| <span style="white-space: nowrap;">`mkdocs build`</span> | Produces the static site in the `site/` directory. The `site/` directory is listed in `.gitignore` and is never committed. |

### 11.5. Deployment

The documentation site is deployed to GitHub Pages via a dedicated GitHub Actions workflow (`.github/workflows/docs.yml`). The workflow:

- **Triggers** on push to `main` when files in `docs/` or `mkdocs.yml` change.
- **Builds** the site using `mkdocs build --strict` (strict mode fails the build on warnings such as broken links or missing pages).
- **Deploys** the built `site/` directory to the `gh-pages` branch using `mkdocs gh-deploy --force`.

The `--strict` flag ensures that documentation quality is enforced in CI. Broken internal links, missing navigation targets, and unreferenced pages cause build failures rather than silent degradation.

### 11.6. Dependencies

`mkdocs` and `mkdocs-material` are added as optional development dependencies in `pyproject.toml` under a `[project.optional-dependencies]` docs group:

```toml
[project.optional-dependencies]
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.5",
]
```

These packages are NOT required for using, developing, or testing metadexer. They are required only for building or previewing the documentation site. Documentation authors install them explicitly with `pip install -e ".[docs]"`.

---

## 12. CLI Interface

### 12.1. Command Structure

The CLI uses `click` as the argument parser. The top-level command is `metadexer`. Subcommands map to module operations:

```
metadexer ingest <target>       # run the sync pipeline on a target directory or file
metadexer search <query>        # query the catalog
metadexer vault verify [...]    # explicit vault verification
metadexer vault prune [...]     # explicit vault pruning
metadexer catalog reconcile     # reconcile catalog against vault
metadexer config [...]          # configuration management
```

### 12.2. CLI Conventions

- Content filtering flags are independent of output destination flags.
- `stdout` stays clean for structured output (JSON). All diagnostics go to `stderr`.
- Destructive operations require explicit opt-in flags.
- `--dry-run` mode is available for any operation with side effects.
- CLI contracts are the canonical interface. API and daemon layers are secondary and MUST NOT implement independent behavior.

---

## 13. Configuration

### 13.1. Configuration Architecture

All configuration uses **TOML** format, parsed by Python's `tomllib` module.

Layered override behavior (lowest to highest priority):

1. Compiled defaults (always present; a Python module, not a TOML file).
2. User config directory (platform-specific; see [§13.2](#132-application-data-directory)).
3. Project-local config (searched upward from target directory).
4. CLI arguments (highest priority).

Configuration objects SHOULD be frozen (immutable) dataclasses. Unknown keys in user-provided TOML MUST be silently ignored (forward compatibility).

### 13.2. Application Data Directory

| Platform | Path |
|----------|------|
| <span style="white-space: nowrap;">Windows</span> | `%LOCALAPPDATA%\metadexer\` |
| <span style="white-space: nowrap;">Linux</span> | `$XDG_CONFIG_HOME/metadexer/` (default: `~/.config/metadexer/`) |
| <span style="white-space: nowrap;">macOS</span> | `~/Library/Application Support/metadexer/` |

### 13.3. Configuration Keys and Defaults

The TOML configuration file mirrors the `MetadexerConfig` frozen dataclass structure. Top-level scalar fields are TOML key-value pairs. Nested structures become TOML tables. The following is a complete example showing every configurable field with its compiled default value. Most users will not need a configuration file at all; the defaults cover the common case.

```toml
# metadexer configuration
# Place this file at:
#   Linux:   ~/.config/metadexer/config.toml
#   macOS:   ~/Library/Application Support/metadexer/config.toml
#   Windows: %LOCALAPPDATA%\metadexer\config.toml
# Or as .metadexer.toml in a project directory for project-local overrides.

# ─── Vault ──────────────────────────────────────────────────────────────────

[vault]
backend = "local"                       # "local" or "s3"
root = ""                               # Vault root path (required for local backend).
                                        # Empty string means unset; must be provided by
                                        # the user or project-local config before use.
chunk_size_bytes = 8388608              # 8 MB. Used for chunked reads/writes and
                                        # streaming hash computation.

[vault.s3]
endpoint_url = ""                       # S3-compatible endpoint URL.
bucket = ""                             # Bucket name.
prefix = ""                             # Optional key prefix within the bucket.
region = ""                             # AWS region (if applicable).
# Credentials are supplied via environment variables (AWS_ACCESS_KEY_ID,
# AWS_SECRET_ACCESS_KEY) or instance profiles. They are never stored in
# this file. See §20.3.

# ─── Catalog ────────────────────────────────────────────────────────────────

[catalog]
backend = "sqlite"                      # "sqlite" or "postgres"

[catalog.sqlite]
path = ""                               # Path to SQLite database file.
                                        # Empty string means unset; defaults to
                                        # <app_data_dir>/catalog.db when not provided.

[catalog.postgres]
# Connection parameters. The connection string is assembled from these fields
# or supplied via the METADEXER_DATABASE_URL environment variable (which takes
# precedence over individual fields). Credentials MUST be supplied via
# environment variables, not stored here. See §20.3.
host = "localhost"
port = 5432
dbname = "metadexer"
# user and password: supplied via PGUSER/PGPASSWORD environment variables.

# ─── Storage Routing ────────────────────────────────────────────────────────

[storage_routing]
inline_max_bytes = 65536                # 64 KB. Content at or below this size (and
                                        # with an eligible MIME type) is stored in the
                                        # vault's inline database surface.
inline_mime_prefixes = ["text/"]         # MIME type prefixes eligible for inline storage.
inline_extra_types = ["application/json"] # Additional full MIME types eligible beyond
                                        # the prefix list.

# ─── Logging ────────────────────────────────────────────────────────────────

[logging]
level = "INFO"                          # Root log level: DEBUG, INFO, WARNING, ERROR.
file_enabled = false                    # Write persistent log files to <app_data_dir>/logs/.
```

Configuration keys not present in the user's TOML file retain their compiled default values. Unknown keys are silently ignored for forward compatibility.

---

## 14. File Encoding and JSON Conventions

### 14.1. File Encoding and Line Endings

All text files in the repository use UTF-8 encoding without BOM and LF (`\n`) line endings. `.gitattributes` enforces `* text=auto eol=lf` to normalize line endings on commit.

### 14.2. JSON Conventions

- All JSON output uses 2-space indentation by default. Compact (no-whitespace) output is available via CLI flag.
- Keys are `snake_case`.
- `null` is used (not omitted) for explicitly absent values on required fields. Optional fields that are `None` are omitted from output.
- Non-ASCII characters are preserved as literal UTF-8, not escaped to `\uXXXX` sequences.
- `orjson` is preferred for performance where available, with `json.dumps()` as a silent fallback.

---

## 15. External Dependencies

### 15.1. Python Dependencies

The full dependency inventory is defined during implementation in `pyproject.toml`. The following are known required dependencies:

| Package | Purpose | Category |
|---------|---------|----------|
| `click` | CLI argument parsing | Required |
| `orjson` | High-performance JSON serialization | Optional (silent fallback to `json` stdlib) |
| `psycopg` (or equivalent) | PostgreSQL database driver | Required for PostgreSQL backend |
| `boto3` (or equivalent) | S3-compatible object storage client | Required for S3 backend |
| `shruggie-indexer` | IndexEntry production | Required (library import preferred; see below) |

**shruggie-indexer invocation method.** The sync module invokes shruggie-indexer via Python library import as the primary method. The indexer's public API exposes `index_path()` ([shruggie-indexer spec §9.2](https://github.com/shruggietech/shruggie-indexer)), which accepts a `Path` and an optional `IndexerConfig` and returns a fully populated `IndexEntry`. This is the default invocation path when `shruggie-indexer` is installed as a Python package (i.e., `from shruggie_indexer import index_path` succeeds).

When the library import is unavailable (e.g., standalone PyInstaller deployments where `shruggie-indexer` is a separate binary on `PATH` rather than an installed Python package), the sync module falls back to subprocess invocation: it calls the `shruggie-indexer` CLI with JSON output mode and parses the resulting IndexEntry JSON from `stdout`. The subprocess fallback produces identical IndexEntry records but incurs per-invocation process startup overhead.

The invocation method is determined at runtime by attempting the library import first. If the import raises `ImportError`, the subprocess path is used. This decision is made once at sync module initialization and cached for the duration of the session. The configuration system does not expose a manual override for this behavior.

### 15.2. External Service Dependencies

| Service | Required | Notes |
|---------|----------|-------|
| PostgreSQL | For PostgreSQL catalog backend | Not required when using SQLite backend |
| S3-compatible storage | For S3 vault backend | Not required when using local filesystem backend |

### 15.3. Dependency Verification at Runtime

| Category | Failure mode |
|----------|-------------|
| Required CLI dependency (e.g., `click`) | Hard error with install instructions. |
| Required backend dependency (e.g., `psycopg`) | Hard error when that backend is selected. |
| Optional performance dependency (e.g., `orjson`) | Silent fallback to stdlib equivalent. |
| Development/test dependency (e.g., `pytest`) | Import error at test time only. |

---

## 16. Logging and Diagnostics

All logging uses Python's standard `logging` module. Logger names follow the package structure (e.g., `metadexer.vault.store`, `metadexer.catalog.ingest`, `metadexer.sync.pipeline`).

Log output goes to `stderr` (console) and optionally to persistent log files under `<app_data_dir>/logs/`. Log files use the naming pattern `YYYY-MM-DD_HHMMSS.log`.

---

## 17. Testing

Test suites are organized by test type, not by source module:

| Category | Directory | Scope |
|----------|-----------|-------|
| <span style="white-space: nowrap;">Unit</span> | `tests/unit/` | Individual functions and methods in isolation. |
| <span style="white-space: nowrap;">Integration</span> | `tests/integration/` | Full pipeline, end-to-end. |
| <span style="white-space: nowrap;">Conformance</span> | `tests/conformance/` | Output structure against canonical schemas and contracts. |
| <span style="white-space: nowrap;">Platform</span> | `tests/platform/` | OS-specific behavior. |

All tests run with a bare `pytest` invocation. `pyproject.toml` registers custom markers with `--strict-markers`. Platform-specific tests use pytest markers (`@pytest.mark.platform_windows`, `@pytest.mark.platform_linux`, `@pytest.mark.platform_macos`) and are executed on the corresponding platform in CI.

---

## 18. Packaging and Distribution

metadexer is **not published to PyPI**. End users download pre-built executables from GitHub Releases.

### 18.1. pyproject.toml Configuration

The complete `pyproject.toml` is the single configuration file for the build system, package metadata, dependency declarations, entry points, and tool settings. The following is the canonical content; an implementer SHOULD produce a file equivalent to this, though field ordering within tables may vary.

```toml
# ─── Build system ───────────────────────────────────────────────────────────

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# ─── Package metadata ──────────────────────────────────────────────────────

[project]
name = "metadexer"
description = "Content-addressed asset management with deep metadata search, hybrid storage routing, and temporal observation tracking"
readme = "README.md"
license = "Apache-2.0"
requires-python = ">=3.12"
authors = [{name = "William Thompson"}]
keywords = ["asset-management", "content-addressed", "metadata", "indexer", "deduplication"]
dynamic = ["version"]
dependencies = [
    "click>=8.1",
    "orjson>=3.9",
    "shruggie-indexer>=0.1.2",
]

[project.optional-dependencies]
postgres = [
    "psycopg[binary]>=3.1",
]
s3 = [
    "boto3>=1.28",
]
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.5",
]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.3",
    "metadexer[postgres,s3]",
]

# ─── Entry points ──────────────────────────────────────────────────────────

[project.scripts]
metadexer = "metadexer.cli:main"

# ─── Hatchling configuration ───────────────────────────────────────────────

[tool.hatch.version]
path = "src/metadexer/_version.py"

[tool.hatch.build.targets.wheel]
packages = ["src/metadexer"]

# ─── Pytest ────────────────────────────────────────────────────────────────

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "platform_windows: marks tests that only run on Windows",
    "platform_linux: marks tests that only run on Linux",
    "platform_macos: marks tests that only run on macOS",
    "requires_postgres: marks tests that require a PostgreSQL instance",
    "requires_s3: marks tests that require an S3-compatible endpoint",
]

# ─── Ruff ──────────────────────────────────────────────────────────────────

[tool.ruff]
target-version = "py312"
line-length = 100
src = ["src"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "RUF",  # ruff-specific rules
]

[tool.ruff.lint.isort]
known-first-party = ["metadexer"]
```

### 18.2. Build and Release Pipeline

Packaging stack:

- `pyproject.toml` as the single metadata and dependency declaration file.
- PyInstaller for standalone executables.
- GitHub Actions release pipeline triggered on `v*` tag pushes, with matrix builds for Windows (x64), Linux (x64), and macOS (arm64).

Release pipeline stages: Checkout, Test, Build (PyInstaller), Rename artifacts (version + platform tags), Upload, Create GitHub Release.

### 18.3. Version Management

The version string lives in a single `_version.py` file:

```python
# src/metadexer/_version.py
__version__ = "0.1.0"
```

All other version consumers read from this file:

| Consumer | Mechanism |
|----------|-----------|
| `pyproject.toml` | `[tool.hatch.version]` reads `__version__` from the file path `src/metadexer/_version.py`. Hatchling parses the file and extracts the version string at build time. |
| `__init__.py` | `from metadexer._version import __version__` makes the version available as `metadexer.__version__` for library consumers. |
| CLI `--version` flag | `@click.version_option(version=__version__)` reads the imported `__version__` attribute. |
| PyInstaller artifacts | The build scripts extract the version from `_version.py` (via a shell `grep`/`sed` or Python one-liner) to construct versioned artifact filenames. |

Versioning follows semantic versioning (`MAJOR.MINOR.PATCH`). Pre-release versions use PEP 440 format in `_version.py` (e.g., `0.1.0rc1`) and hyphenated form in git tags (e.g., `v0.1.0-rc1`). During the `0.x.y` series, minor version bumps MAY include breaking changes.

---

## 19. Platform Portability

### 19.1. Cross-Platform Design Principles

Design goal G9 ([§2.3](#23-design-goals)) states: the application MUST run on Windows, Linux, and macOS from a single codebase. The following principles govern the approach to platform portability:

**No platform-conditional logic in the core modules.** The `vault/`, `catalog/`, and `sync/` subpackages MUST NOT contain `if sys.platform == ...` or `if os.name == ...` branches. All platform variation is absorbed by Python standard library abstractions (`pathlib`, `os`, `hashlib`, `subprocess`) or by the configuration system. The one permitted exception is the `cli.py` entry point, which MAY contain platform-conditional logic for presentation-layer concerns (console encoding, terminal setup) that do not affect application behavior.

**Forward-slash normalization in stored paths.** All path strings stored in the catalog use forward-slash (`/`) separators, regardless of the host platform. This ensures that catalog data is portable across operating systems.

**Graceful degradation for unavailable features.** When a platform does not support a feature, the application uses the best available approximation and logs a debug-level message on first occurrence. No per-file warnings are produced for known platform limitations.

### 19.2. Platform-Specific Considerations

**Windows.** The application data directory resolves under `%LOCALAPPDATA%` (Local), not `%APPDATA%` (Roaming). Long path support (`\\?\` prefix) is handled by Python's `pathlib` where applicable. Console output encoding is set to UTF-8 explicitly.

**Linux.** The application data directory follows the XDG Base Directory Specification, defaulting to `~/.config/` when `XDG_CONFIG_HOME` is not set.

**macOS.** The application data directory resolves to `~/Library/Application Support/`. The arm64 architecture is the primary macOS build target.

Platform-specific behaviors are verified by the `tests/platform/` test suite ([§17](#17-testing)).

---

## 20. Security and Safety

### 20.1. Path Validation and Sanitization

All user-supplied path inputs MUST be resolved to canonical absolute paths before use. The application MUST NOT follow symbolic links into directories outside the user-specified target scope unless explicitly directed. Path traversal attacks (e.g., `../../etc/passwd` embedded in filenames or metadata) MUST be detected and rejected.

Vault storage keys are derived from `storage_name` values produced by the indexer (deterministic, content-derived, alphanumeric with a single dot separator). The vault backend MUST validate that storage keys conform to the expected pattern before performing any filesystem or object storage operation.

### 20.2. Destructive Operation Safeguards

All destructive operations require explicit opt-in flags. This applies to vault prune, reference deletion, catalog entry removal, and any operation that modifies or removes stored data. No destructive action is ever a default. `--dry-run` mode is available for any operation with side effects, and `--dry-run` MUST be the default behavior for prune operations unless an explicit confirmation flag is provided.

### 20.3. Credential and Secret Handling

Database connection strings, S3 access keys, and other credentials MUST NOT be stored in plaintext configuration files. Credentials are supplied via environment variables or platform-native credential storage mechanisms. Configuration files MAY reference environment variable names but MUST NOT contain credential values directly. Credentials MUST NOT appear in log output at any log level.

### 20.4. Large File and Resource Limit Handling

The vault module handles files of arbitrary size. File content MUST be read and written in chunks (not loaded entirely into memory) to prevent memory exhaustion on large objects. Hash computation during verification MUST use streaming (chunked) reads. The catalog module MUST handle IndexEntry records of arbitrary depth (deeply nested directory trees with large `items` arrays) without stack overflow. Configurable limits on batch sizes and concurrent operations prevent resource exhaustion during bulk ingestion.

---

## 21. Performance Considerations

### 21.1. Ingestion Pipeline Performance

The ingestion pipeline is designed for throughput at scale (millions of files, terabytes of data). Deduplication checks against the catalog and vault MUST be performed before any byte transfer to avoid redundant I/O. Batch operations (catalog commits, vault existence checks) SHOULD be used where the backend supports them to minimize round-trip overhead.

### 21.2. Catalog Query Performance

The catalog schema MUST include appropriate indexes on commonly queried fields: `id`, `mime_type`, `size.bytes`, `timestamps.modified`, `name.text`, and `extension`. Full-text search over string-stored content uses the database engine's native full-text search capabilities (PostgreSQL `tsvector`/`tsquery`, SQLite FTS5). Index design is documented as part of the catalog backend implementation.

### 21.3. Vault I/O Performance

Vault operations use chunked I/O for all file reads and writes. The chunk size is configurable with a sensible default (8 MB, per the `vault.chunk_size_bytes` configuration key in [§13.3](#133-configuration-keys-and-defaults)). For the S3 backend, multipart upload is used for objects exceeding the S3 single-upload size threshold. The local filesystem backend uses the two-character prefix sharding scheme defined in [§5.3](#53-storage-backends) to prevent performance degradation from directories with millions of entries.

---

## 22. Development Phases

Phase 1 (Foundation) is complete: shruggie-indexer v0.1.2 is released and stable. The following phases define the remaining implementation ordering.

### 22.1. Phase 2: Storage and Catalog

**Target:** A working local-mode system where `metadexer ingest <directory>` indexes files, stores bytes in a local vault, and commits metadata to a catalog with basic query support.

Scope:

- Vault module: put, get, head, verify. Local filesystem backend first. S3-compatible backend second. Inline database surface for small text-based content.
- Catalog module: IndexEntry ingest, field projection, basic search (MIME type, size, timestamps, name, extension). PostgreSQL backend as primary target. SQLite backend for portable/evaluation use. Full-text search indexing of vault-stored inline content.

Deferred from this phase: reference tracking (collections/projects/users), temporal correlation, reconciliation, pruning.

### 22.2. Phase 3: Pipeline

**Target:** A reliable, resumable ingestion pipeline with dry-run support.

Scope:

- Sync Plan generation (dry-run preview of pending operations).
- Deduplication checks against existing catalog/vault state.
- Storage routing based on configurable rulesets.
- Resumable operation across interrupted runs.
- Idempotent catalog commits.

### 22.3. Phase 4: Search and Scale

**Target:** Full catalog capabilities as specified in [§6](#6-catalog-module).

Scope:

- Full-text search over string-stored content.
- Reference tracking (collections, projects, tenants).
- Temporal correlation of IndexEntry snapshots.
- Vault reconciliation (detect orphaned or missing blobs).
- Vault pruning for unreferenced objects.

### 22.4. Phase 5: Integration and Polish

Scope:

- hotwire integration (automated feed ingestion pipeline).
- Web UI for search and browsing (thin layer over API).
- MEGA S4 as a vault backend.
- Documentation site, public release, metadexer.com.

---

## 23. Development Workflow

### 23.1. Purpose and Authority

This section defines the standardized development workflow for the metadexer project. It governs how administrative planning, coding, review, and integration are conducted across all development sessions. All participants (human and AI agents) MUST follow this workflow unless an explicit, documented exception is approved by the project lead.

This workflow supersedes all ad-hoc development patterns previously used on the project. It incorporates parallel agent execution, worktree-based isolation, and a structured handoff protocol between strategic planning and implementation.

### 23.2. Workflow Layers

Development activity is organized into two distinct layers. These layers operate independently and communicate through version-controlled artifacts only. No direct, informal channel (verbal, chat, or otherwise) substitutes for the written handoff artifacts described in [§23.3](#233-handoff-protocol).

#### 23.2.1. Admin Layer

The admin layer is responsible for strategic direction, specification authoring, sprint planning, brainstorming, and roadblock resolution. It operates in browser-based AI chat sessions (Claude.ai projects, or equivalent) where rich project history and personal context are available.

**Outputs produced by the admin layer:**

| Artifact | Description | Destination |
|----------|-------------|-------------|
| Technical specifications | `metadexer-spec.md`, `shruggie-indexer-spec.md`. The authoritative source of truth for all architectural and behavioral decisions. | Repository root |
| Sprint planning documents | Structured work item definitions following the five-section format from the metadexer overview (Appendix D): header block, purpose and context, implementation ordering, work item sections, and specification update directive. | `.handoff/plans/` |
| Agent context files | `CLAUDE.md` and `.github/copilot-instructions.md`. Persistent project-level context consumed by AI coding agents. See [§23.6.1](#2361-agent-context-files). | Repository root and `.github/` respectively |
| Workflow updates | Updates to this specification's [§23](#23-development-workflow) section when process changes are needed. | Repository root (within `metadexer-spec.md`) |

The admin layer MUST NOT make direct code changes. All implementation flows through the coding layer.

#### 23.2.2. Coding Layer

The coding layer is responsible for implementing the work defined by the admin layer. It operates in IDE-based and terminal-based AI coding agent sessions (Claude Code, VS Code background/cloud agents, or equivalent tools).

**Inputs consumed by the coding layer:**

| Artifact | Source | How it is obtained |
|----------|--------|--------------------|
| <span style="white-space: nowrap;">Sprint planning document</span> | `.handoff/plans/` | The project lead provides the file path or pastes the content into the agent's context window. The agent reads it from the repository if operating in a worktree with the latest `main` state. |
| <span style="white-space: nowrap;">Technical specification</span> | Repository root | The agent reads the specification file for the component under modification. The project lead MAY explicitly include it in the context window or instruct the agent to read it. |
| <span style="white-space: nowrap;">Agent context file</span> | `CLAUDE.md` (auto-read by Claude Code) or `.github/copilot-instructions.md` (auto-read by GitHub Copilot) | Loaded automatically by the tool at session start. No manual step required. |
| <span style="white-space: nowrap;">Current codebase state</span> | Git repository | The agent inspects the repository independently. Agents MUST NOT assume the codebase matches any prior description; they verify it directly using grep, file reads, and test execution. |

**Outputs produced by the coding layer:**

| Artifact | Description | Destination |
|----------|-------------|-------------|
| <span style="white-space: nowrap;">Code changes</span> | Committed to the repository per the git conventions in [§23.5](#235-git-conventions). | Git repository (committed to branch or `main`) |
| <span style="white-space: nowrap;">Test results</span> | Pass/fail status and coverage deltas. Recorded in the session report. | `.handoff/reports/` (within the session report) |
| <span style="white-space: nowrap;">Changelog entries</span> | Additions to `CHANGELOG.md` reflecting completed work. | Repository root |
| <span style="white-space: nowrap;">Session report</span> | A structured summary of the session's activities, results, and observations. See [§23.3.4](#2334-session-report-format). | `.handoff/reports/` |

The coding layer MUST NOT make architectural decisions, redefine module boundaries, or deviate from the specification without explicit authorization from the admin layer.

### 23.3. Handoff Protocol

The handoff protocol is the critical integration point between layers. All task definitions and results MUST pass through written, version-controlled artifacts. This section defines the directory structure, artifact formats, and procedures for both directions of handoff.

#### 23.3.1. Handoff Directory Structure

```
.handoff/
├── plans/        # Admin → Coding (sprint docs)
└── reports/      # Coding → Admin (session reports, test summaries)
```

Both subdirectories use the standard ShruggieTech naming convention: `<YYYYmmdd>-<ZZZ>-<title>.<ext>`, where `ZZZ` is a three-digit zero-padded increment that resets to `001` on each new date.

The `.handoff/` directory is tracked in version control. All artifacts committed here become part of the project's permanent record. When a sprint is fully complete and its reports have been reviewed, the associated plan and report files MAY be moved to `.archive/` to keep `.handoff/` focused on active or recent work.

#### 23.3.2. Admin-to-Coding Handoff

The admin layer produces the following artifacts and commits them to `.handoff/plans/`:

**Sprint document.** A markdown file following the five-section structure defined in the metadexer overview (Appendix D). The document contains:

1. **Header block.** Sprint identifier (date-increment format), target component, target phase, and estimated scope.
2. **Purpose and context.** What this sprint achieves and why it matters. References to specification sections that govern the work.
3. **Implementation ordering.** The sequence in which work items MUST be executed, with dependency declarations between items.
4. **Work item sections.** Each work item is a self-contained unit with: a description of the task, a list of affected files (the "affected file matrix"), specific implementation instructions, and acceptance criteria expressed as verifiable commands or assertions.
5. **Specification update directive.** Instructions for any specification changes that should accompany the code changes (if applicable).

Each work item section MUST be written so that an AI coding agent can execute it within a single context window, without interactive clarification. If a work item requires more context than fits in a single window, it MUST be decomposed into smaller items.

**Procedure:**

1. The admin layer authors the sprint document.
2. The sprint document is committed to `.handoff/plans/` with the message: `workflow: add sprint <YYYYMMDD>-<ZZZ>`.
3. The project lead pushes the commit to `main` (or merges it if authored on a branch).
4. The coding layer pulls `main` and reads the sprint document to initiate work.

#### 23.3.3. Coding-to-Admin Handoff

When a coding session concludes (whether the sprint is complete, partially complete, or blocked), the coding layer produces a session report and commits it to `.handoff/reports/`.

**What gets committed:**

1. **Session report** (required). A structured markdown file following the format in [§23.3.4](#2334-session-report-format).
2. **Changelog update** (required if work was completed). Additions to `CHANGELOG.md` at the repository root.
3. **Test evidence** (required if tests were executed). Test output MAY be embedded in the session report or committed as a separate file alongside it.

**Procedure:**

1. The coding agent (or the project lead on the agent's behalf) authors the session report.
2. The session report is committed to `.handoff/reports/` with the message: `workflow: add session report <YYYYMMDD>-<ZZZ>`.
3. If the agent cannot generate the report itself (due to tool limitations), the project lead authors it manually based on the agent's commit history and test output. The report MUST still follow the defined format.
4. The admin layer reviews the session report, the commit history, the changelog, and the test results before initiating the next planning cycle.

#### 23.3.4. Session Report Format

Every session report is a markdown file committed to `.handoff/reports/`. The filename follows the standard naming convention (e.g., `20260310-001-sprint-001-session-report.md`). The file MUST contain the following sections in order:

````markdown
# Session Report: <Sprint ID>, <Work Item(s)>

- **Date:** <YYYY-MM-DD>
- **Agent:** <tool name and mode, e.g., "Claude Code interactive", "VS Code Background Agent">
- **Sprint reference:** <path to sprint document in .handoff/plans/>
- **Work items addressed:** <comma-separated list of item numbers>
- **Status:** <Complete | Partial | Blocked>

## Changes Made

<A file-level summary of all modifications. For each file changed, state what was
done and why. This is not a diff; it is a human/AI-readable narrative of the changes.>

## Test Results

<Pass/fail summary. Include the exact pytest invocation and its output summary line.
If coverage was measured, include the delta. Example:>

```
$ pytest
====== 47 passed in 3.21s ======
```

## Deviations from Sprint Plan

<Any cases where the agent deviated from the sprint document's instructions.
Each deviation MUST state what was specified, what was done instead, and why.
If no deviations occurred, state "None.">

## Issues and Observations

<Anything the admin layer should be aware of: bugs discovered, ambiguities in the
specification, performance concerns, suggestions for future work. If none, state "None.">
````

The session report is the primary mechanism by which the admin layer gains visibility into what happened during a coding session. It MUST be accurate and complete enough that the admin layer can make informed planning decisions without re-reading every commit diff.

#### 23.3.5. Agent Session Transcript Preservation

Agent session transcripts (the full conversation log between a human or orchestrator and the AI coding agent) are a valuable debugging and auditing resource. However, transcript export mechanisms vary by tool:

| Tool | Transcript access |
|------|-------------------|
| <span style="white-space: nowrap;">Claude Code (interactive)</span> | Conversation history is accessible via the Claude Code CLI. Export by copying the session log or using built-in export commands if available. |
| <span style="white-space: nowrap;">VS Code Background Agent</span> | Session logs are accessible via the Chat panel history. Content can be copied from the panel. |
| <span style="white-space: nowrap;">VS Code Cloud Agent</span> | Session logs are accessible via the GitHub Copilot interface. |
| <span style="white-space: nowrap;">Superset</span> | Per-agent transcripts are accessible via the Superset task view. |

Transcripts are NOT committed to the repository by default (they are typically too large and contain tool-specific formatting). Instead, the project lead preserves them locally when needed for debugging. The session report ([§23.3.4](#2334-session-report-format)) serves as the lightweight, version-controlled summary of what occurred.

When a transcript is needed for debugging agent behavior, the project lead extracts the relevant portions and includes them in the session report's "Issues and Observations" section, or files them as a separate document in `.handoff/reports/` with a descriptive filename (e.g., `20260310-002-transcript-excerpt-vault-bug.md`).

### 23.4. Agent Execution Model

The coding layer supports three execution modes. The project lead selects the appropriate mode based on task characteristics.

#### 23.4.1. Sequential Mode

A single agent session processes one work item at a time. The agent operates directly on the main branch. Changes are reviewed and committed before the next work item begins.

**When to use:** Simple, low-risk changes. Bug fixes with narrow scope. Specification updates. Tasks where the overhead of worktree setup exceeds the time saved by parallelism.

**Procedure:**

1. Open a coding agent session (VS Code local agent, Claude Code interactive, or equivalent).
2. Provide the sprint document and template as context.
3. The agent implements the work item.
4. Review the changes. Run acceptance criteria verification commands from the sprint document.
5. Commit to main. Proceed to the next work item.

#### 23.4.2. Parallel Independent Mode

Multiple agent sessions run simultaneously, each in an isolated Git worktree on a separate branch. Agents work on independent tasks and cannot interfere with each other.

**When to use:** Two or more work items from the same sprint are independent (no shared file modifications, no sequential dependency). Tasks are well-defined and self-contained. Time savings from parallelism justify the merge overhead.

**Procedure:**

1. Identify independent work items in the sprint document. Verify independence by checking the "affected file matrix" in each work item section. If two items modify the same file, they are NOT independent and MUST be executed sequentially.
2. For each independent work item, start a separate agent session in its own worktree:
   - **Using VS Code:** Start a Background Agent session per task (Chat view > New Chat (+) > New Background Agent > select "Worktree" isolation).
   - **Using Superset:** Create a new task (Cmd+T) per work item. Superset handles worktree creation automatically.
   - **Using Claude Code directly:** Use the `--worktree` flag or `isolation: worktree` in the agent definition.
3. Provide each agent with: the relevant work item section from the sprint document, the specification, and the `CLAUDE.md` context file.
4. Monitor agent progress. Intervene only if an agent requests clarification or stalls.
5. When an agent completes, review the diff against the sprint document's acceptance criteria. Run the specified verification commands.
6. Merge completed branches into main one at a time, in the dependency order specified by the sprint document's implementation ordering section:
   ```bash
   git checkout main
   git merge --no-ff <branch-name>
   ```
   If using VS Code background agents, use the "Apply" action in the Chat view instead of manual merge commands.
7. After each merge, verify that the cumulative codebase passes all tests before proceeding to the next merge.
8. Delete completed worktrees after successful merge.

**Branch naming convention:**

```
sprint/<YYYYMMDD>-<ZZZ>/<work-item-number>-<short-description>
```

Example: `sprint/20260310-001/03-vault-put-operation`

#### 23.4.3. Coordinated Team Mode

A lead agent decomposes a complex task and delegates subtasks to multiple subordinate agents that can communicate with each other. This mode is experimental and carries significantly higher token costs.

**When to use:** Complex tasks that benefit from multiple perspectives operating on the same logical problem (e.g., parallel exploration of architecture options, simultaneous implementation and test writing for a tightly coupled module). Reserved for tasks where the cost is justified by the complexity.

**Procedure (Claude Code Agent Teams):**

1. Verify the `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` environment variable is set to `1`.
2. Start a Claude Code session and describe the task, specifying how many teammates to spawn and what each should focus on.
3. The lead agent coordinates work through a shared task list. Monitor progress in split-pane terminal mode (requires tmux or iTerm2).
4. Review the combined output. The lead agent synthesizes results from all teammates.
5. Commit the coordinated result to main (or to a worktree branch for review first).

**Cost expectation:** Approximately 5x the token usage of a single-agent session per spawned teammate. Use sparingly and only for tasks where the coordination overhead produces measurably better outcomes.

### 23.5. Git Conventions

#### 23.5.1. Branch Strategy

The project uses a single `main` branch as the integration target. All work, whether executed sequentially or in parallel, merges to `main`.

Feature branches exist only as temporary worktree branches during parallel execution. They are deleted after merge. Long-lived feature branches are not used.

#### 23.5.2. Commit Discipline

- Each logical change is one commit. Agents SHOULD NOT bundle unrelated changes into a single commit.
- Commit messages follow the pattern: `<module>: <imperative description>` (e.g., `vault: implement put operation for local backend`).
- Sprint-related commits MAY reference the sprint document in the message body: `Sprint: 20260310-001, Item 3`.
- Merge commits from parallel branches use `--no-ff` to preserve branch history in the log.

#### 23.5.3. Worktree Cleanup

After a successful merge, the worktree and its branch MUST be deleted:

```bash
git worktree remove <path>
git branch -d <branch-name>
```

If using Superset or VS Code, worktree cleanup is handled automatically when you dismiss a completed task or delete an agent session.

### 23.6. Agent Context Management

#### 23.6.1. Agent Context Files

The repository maintains two agent context files that provide persistent project-level context to AI coding agents. Both files are the admin layer's responsibility to maintain and keep synchronized.

**`CLAUDE.md`** at the repository root. Read automatically by Claude Code at session start. This is the primary agent context file.

**`.github/copilot-instructions.md`** in the `.github/` directory. Read automatically by GitHub Copilot in VS Code. This is the secondary agent context file.

**Required contents (identical in both files):**

- Project identity: name (`metadexer`), organization (`ShruggieTech LLC`), language (`Python 3.12+`).
- Repository structure summary: top-level directory layout with one-line descriptions.
- Specification location and authority hierarchy: `metadexer-spec.md` is authoritative for metadexer; `shruggie-indexer-spec.md` (in the indexer repo) is authoritative for the indexer. The specification overrides all other documents when they conflict.
- Coding conventions: UTF-8 without BOM, LF line endings, `snake_case` for Python identifiers, `import` ordering (`stdlib` / `third-party` / `local`), standard `logging` module usage.
- Testing conventions: `pytest` invocation, `--strict-markers`, test directory structure by type ([§17](#17-testing)).
- CLI conventions: `click` for argument parsing, `stdout` for structured output, `stderr` for diagnostics, `--dry-run` for side-effecting operations.
- Explicit prohibitions: no silent data loss, no implicit deletion, no recomputing identity, no architectural decisions without admin layer authorization.

**Tool-specific preamble (differs between files):**

Each file MAY include a brief preamble at the top with instructions specific to the tool that reads it. For example, `CLAUDE.md` may include Claude Code-specific conventions for tool use or file handling. `.github/copilot-instructions.md` may include Copilot-specific conventions for suggestion behavior. The preamble MUST NOT contradict the shared core content.

**Synchronization rule:** When the admin layer updates one file, it MUST update the other in the same commit. The commit message for agent context updates is: `docs: update agent context files`.

**Canonical file contents:**

The following are the literal file contents to be committed to the repository. The shared core section is identical in both files; only the tool-specific preamble differs.

**`CLAUDE.md`:**

````markdown
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
│   ├── vault/          # Content-addressed storage (files and inline text)
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
````

**`.github/copilot-instructions.md`:**

````markdown
# Copilot Instructions — metadexer

<!-- This file is read automatically by GitHub Copilot in VS Code. -->
<!-- It provides persistent project-level context for code suggestions. -->
<!-- Do not modify during coding sessions. Admin layer manages this file. -->

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
│   ├── vault/          # Content-addressed storage (files and inline text)
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
````

#### 23.6.2. Sprint Document as Agent Context

When executing a work item, the coding agent's context MUST include:

1. The agent context file (`CLAUDE.md` or equivalent) -- always.
2. The specific work item section from the sprint document -- always.
3. The authoritative specification for the component being modified -- always.
4. Any referenced prior sprint documents or changelogs -- only when the work item explicitly depends on prior work.

Agents MUST NOT be given the entire sprint document if they are only executing one work item. Unnecessary context degrades agent performance and increases cost.

#### 23.6.3. Agent Session Discipline

- Agents MUST NOT trust prior implementation work without independent verification.
- Agents MUST use grep-based evidence collection to verify codebase state before making changes.
- Agents MUST verify acceptance criteria against actual runtime behavior, not assumed correctness from code inspection alone.
- Each work item section is self-contained. An agent implementing Item 3 MUST NOT assume that Item 2 has been completed unless the sprint document's implementation ordering explicitly establishes that dependency and the agent has verified the dependency is satisfied in the current codebase.

### 23.7. Review and Integration

#### 23.7.1. Review Checklist

Before merging any agent-produced changes (whether from sequential or parallel execution), the project lead verifies:

1. **Acceptance criteria:** Every criterion listed in the sprint document's work item is met, verified by running the specified commands.
2. **Specification compliance:** Changes conform to the authoritative specification. No new behavior is introduced that the specification does not define or permit.
3. **Test passage:** `pytest` runs clean with no failures or unexpected warnings.
4. **Encoding:** All new or modified files use UTF-8 without BOM and LF line endings. Spot-check with `file --mime-encoding <path>`.
5. **No scope creep:** Changes are limited to what the sprint document authorized. Agents occasionally introduce "helpful" improvements outside the defined scope; these are reverted or deferred to a future sprint.
6. **Changelog:** `CHANGELOG.md` reflects the changes accurately.

#### 23.7.2. Merge Conflict Resolution

When merging parallel branches, conflicts may arise if:

- Two agents modified the same file despite the affected file matrix indicating independence (an error in the sprint document).
- An agent modified a shared dependency (e.g., `__init__.py` imports, `pyproject.toml` dependencies).

Conflict resolution is the project lead's responsibility. Resolution follows these rules:

- If both changes are correct and non-overlapping within the file, combine them manually.
- If the changes are logically conflicting (two different approaches to the same problem), choose one and file a follow-up item for the discarded approach if needed.
- After resolving conflicts, re-run the full test suite to verify the combined result.

### 23.8. Tooling Configuration

#### 23.8.1. Recommended Stack

| Layer | Primary Tool | Alternative |
|-------|-------------|-------------|
| <span style="white-space: nowrap;">Admin</span> | Claude.ai (Project-based) | Any browser-based AI chat with persistent context |
| <span style="white-space: nowrap;">Coding (interactive)</span> | VS Code Local Agent or Claude Code (interactive) | Any IDE with integrated AI chat |
| <span style="white-space: nowrap;">Coding (parallel)</span> | Superset + Claude Code | VS Code Background Agents |
| <span style="white-space: nowrap;">Coding (cloud/CI)</span> | VS Code Cloud Agent (Copilot coding agent) | Claude Code on web (claude.ai/code) |
| <span style="white-space: nowrap;">Review</span> | VS Code (final codebase), Superset (per-agent diffs) | `git diff` on the command line |

#### 23.8.2. VS Code Configuration

The following VS Code settings are recommended for multi-agent workflows:

```json
{
  "chat.agent.enabled": true,
  "github.copilot.chat.claudeAgent.enabled": true,
  "editor.formatOnSave": true,
  "files.encoding": "utf8",
  "files.eol": "\n"
}
```

#### 23.8.3. Superset Configuration

If Superset is used for orchestration, the repository SHOULD include a `.superset/` directory with:

```
.superset/
├── config.json
├── setup.sh
└── teardown.sh
```

**config.json:**
```json
{
  "setup": ["./.superset/setup.sh"],
  "teardown": ["./.superset/teardown.sh"]
}
```

**setup.sh:**
```bash
#!/bin/bash
# Copy environment variables from the root worktree
cp ../.env .env 2>/dev/null || true
# Install development dependencies
pip install -e ".[dev]" --quiet
echo "Worktree ready."
```

**teardown.sh:**
```bash
#!/bin/bash
echo "Worktree cleanup complete."
```

### 23.9. Workflow Summary

The following sequence describes one complete development cycle from planning through integration.

1. **Admin layer** reviews the current state of the project (recent commits, test results, session reports in `.handoff/reports/`).
2. **Admin layer** authors a sprint document defining the next batch of work items. The document follows the five-section structure.
3. **Admin layer** commits the sprint document to `.handoff/plans/`.
4. **Project lead** reviews the sprint document's work items and determines the execution mode:
   - If all items are sequential dependencies: use Sequential Mode ([§23.4.1](#2341-sequential-mode)).
   - If some items are independent: use Parallel Independent Mode ([§23.4.2](#2342-parallel-independent-mode)) for independent items, Sequential Mode for dependent items.
   - If a single complex item benefits from multi-perspective exploration: use Coordinated Team Mode ([§23.4.3](#2343-coordinated-team-mode)).
5. **Coding layer** executes work items per the selected mode.
6. **Coding layer** produces session report(s) and commits them to `.handoff/reports/`.
7. **Project lead** reviews agent output per the Review Checklist ([§23.7.1](#2371-review-checklist)).
8. **Coding layer** merges approved changes to main.
9. **Project lead** verifies the cumulative codebase state (full test suite, encoding checks).
10. **Admin layer** consumes the coding layer's output (session reports, commits, changelog, test results) and begins planning the next cycle.

---

## 24. Composition Rules

No module MAY:

- Recompute identity unless performing an explicit integrity verification.
- Rewrite or amend an IndexEntry outside of the indexer's own operation.
- Implicitly delete content from any backend.
- Implicitly migrate content between backends.

Cross-module interaction within metadexer occurs through defined internal APIs. The indexer communicates with metadexer exclusively through the IndexEntry JSON contract.

---

## 25. Future Considerations

The following capabilities are achievable through future extension without requiring changes to the identity model or core contracts:

- Multiple vault backends operating simultaneously.
- Multiple catalog instances (e.g., per-tenant, per-project).
- Vault-to-vault migration with integrity verification.
- Manifest export and import for portable asset sets.
- Snapshot materialization from catalog state.
- Immutable archival tiers with tiered access policies.
- A web-based UI layer for search and browsing (API-driven, thin over CLI logic).
- Integration with hotwire for automated real-time feed ingestion.
- Embedding and vector search extensions for semantic retrieval.

None of these capabilities require redefining content identity. The IndexEntry contract is the stable foundation on which all future extension is built.

---

## Document History

| Date | Version | Change |
|------|---------|--------|
| <span style="white-space: nowrap;">2026-03-07</span> | DRAFT | Initial specification. Derived from the metadexer high-level overview (`20260305-004-metadexer-overview.md`). Establishes architectural contracts, module responsibilities, invariants, and development phasing sufficient for sprint planning. |
| <span style="white-space: nowrap;">2026-03-09</span> | DRAFT | Merged the standalone development workflow document (`metadexer-development-workflow.md`, dated 2026-03-08) into the specification as §23. Expanded handoff protocol with concrete artifact formats, session report schema, and agent session transcript preservation guidance. Introduced `.handoff/plans/` and `.handoff/reports/` directory structure, replacing the prior use of `.archive/` as the handoff location. `.archive/` is retained for historical document storage only. Added `CLAUDE.md` and `.github/copilot-instructions.md` as defined agent context files with synchronization requirements. Updated repository structure (§10) to reflect new directories and files. Added workflow-related terms to the terminology table (§1.5). Renumbered §23 (Composition Rules) to §24 and §24 (Future Considerations) to §25. |
| <span style="white-space: nowrap;">2026-03-19</span> | DRAFT | Pre-Sprint 1 gap resolution pass. Added catalog database schema for PostgreSQL and SQLite (§6.8). Added canonical `pyproject.toml` configuration (§18.1) and version management details (§18.3). Added literal agent context file contents for `CLAUDE.md` and `.github/copilot-instructions.md` (§23.6.1). Added configuration TOML structure with all Phase 2 keys and defaults (§13.3). Added default storage routing thresholds and ruleset (§6.5). Specified vault local backend directory layout with two-character prefix sharding (§5.3). Defined shruggie-indexer invocation method as library-first with subprocess fallback (§15.1). Clarified vault `get` operation accepts `storage_name` only, not `id` (§5.2). Resolved license field contradiction in §10.1. Removed hedging language from CLI subcommand tree (§12.1). Specified changelog copy automation as a docs CI build step (§11.3). Updated §21.3 to reference concrete sharding and chunk size specifications. |
| <span style="white-space: nowrap;">2026-03-19</span> | DRAFT | Retired `_TEMPLATE.txt` session prompt template convention from §23. Sprint documents are the sole admin-to-coding handoff artifact. Removed template references from §10.1, §23.2.1, §23.3.1, §23.3.2, §23.6.2, and §23.9. |
| <span style="white-space: nowrap;">2026-03-19</span> | DRAFT | Pre-Sprint 2 gap resolution: added vault backend interface (§5.4). Defined `VaultBackend` abstract base class with method signatures for put, get, head, delete, open_read, and iter_storage_names. Defined `VaultStore` facade with deduplication, streaming hash verification, and prune orchestration. Defined `VerifyResult` and `PruneResult` frozen dataclasses. Renumbered §5.4 (Invariants) to §5.5 and §5.5 (Verification Modes) to §5.6. Updated all cross-references. |
| <span style="white-space: nowrap;">2026-03-19</span> | DRAFT | Pre-Sprint 2 gap resolution: added catalog backend interface (§6.4). Defined `CatalogBackend` abstract base class with method signatures for initialize_schema, upsert_asset, get_by_id, get_by_storage_name, search, count, iter_all_storage_names, and close. Defined `CatalogIngestor` (write-path) and `CatalogSearcher` (read-path) facade classes. Defined shared types: `AssetRecord`, `SearchQuery`, `SearchResult`, and `IngestResult` as frozen dataclasses. Renumbered §6.4 (Hybrid Storage Routing) through §6.7 (Catalog Database Schema) to §6.5 through §6.8. Updated all cross-references. |
| <span style="white-space: nowrap;">2026-03-19</span> | DRAFT | Pre-Sprint 2 gap resolution: added exception hierarchy (§9.3). Defined `MetadexerError` base class with module-scoped subtypes: `ConfigurationError`, `VaultError` (with `VaultObjectNotFoundError`, `VaultHashCollisionError`, `VaultIOError`), `CatalogError` (with `CatalogIngestError`, `CatalogConnectionError`, `CatalogSchemaError`), and `SyncError` (with `IndexerInvocationError`, `SyncPipelineError`). Added CLI exit code mapping (§9.3.1) and exception chaining convention (§9.3.2). Added `exceptions.py` to the source package layout in §10.2. |
| <span style="white-space: nowrap;">2026-03-19</span> | DRAFT | Pre-Sprint 2 gap resolution: added SQL trigger definitions to catalog database schema (§6.8). PostgreSQL: added `assets_search_vector_update()` function and `trg_assets_search_vector` trigger for tsvector maintenance with weighted A/B ranking on name_text and inline_content. SQLite: added `trg_assets_fts_insert`, `trg_assets_fts_delete`, and `trg_assets_fts_update` triggers for FTS5 content-external table synchronization. |
| <span style="white-space: nowrap;">2026-03-19</span> | DRAFT | Architectural change: moved inline text content storage from the catalog module to the vault module. The vault is now the sole owner of all stored content (file-based and inline text). Added vault inline database surface (§5.4.4) with `VaultInlineStore` class and `vault_inline` table schema for both PostgreSQL and SQLite. Added `vault/inline.py` to source package layout (§10.2). Split §5.2 into §5.2.1 (file-based operations) and §5.2.2 (inline operations) with `put_inline` and `get_inline`. Updated `VaultStore` facade (§5.4.2) with `inline_store` parameter and inline methods. Expanded §5.3 (Storage Backends) and §5.5 (Invariants) to cover both storage surfaces. Removed `inline_content` column from catalog `assets` table in both PostgreSQL (§6.8.1) and SQLite (§6.8.2) schemas. Removed `inline_content` field from `AssetRecord` (§6.4.3). Replaced PostgreSQL trigger-based tsvector maintenance with application-side computation at INSERT time (§6.8.1). Switched SQLite FTS5 from content-external mode to standalone mode (§6.8.2). Renamed `CatalogIngestor.ingest()` parameter from `inline_content` to `search_text` (§6.4.2) and added `search_text` parameter to `CatalogBackend.upsert_asset()` (§6.4.1). Renamed §6.5 from "Hybrid Storage Routing" to "Storage Routing" and reframed as vault-internal routing. Updated §1.5 (Vault terminology), §3.1 (Component Map), §3.2 (Module Responsibilities), §3.3 (Data Flow), §6.7 (Invariants), §6.8.3 (Schema Notes), §7.2 (Pipeline Stages), and §22.1 (Phase 2 scope). |
| <span style="white-space: nowrap;">2026-03-19</span> | DRAFT | Sprint 003 cleanup: removed stale "Session prompt template" row from §23.2.2. Updated §1.2 scope descriptions and §23.6.1 agent context file content to reflect vault-owned inline storage architecture. Added `config.py` to §10.2 source package layout. |
