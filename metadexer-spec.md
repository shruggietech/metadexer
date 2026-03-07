<a id="metadexer-technical-specification"></a>
# metadexer — Technical Specification

- **Project:** `metadexer`
- **Domain:** metadexer.com (reserved)
- **Repository:** TBD (not yet created)
- **License:** TBD
- **Version:** Pre-release (0.1.0 target)
- **Author:** William Thompson (ShruggieTech LLC)
- **Date:** 2026-03-07
- **Status:** DRAFT
- **Audience:** AI-first, Human-second

---

<a id="table-of-contents"></a>
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
  - [5.3. Storage Backends](#53-storage-backends)
  - [5.4. Invariants](#54-invariants)
  - [5.5. Verification Modes](#55-verification-modes)
- [6. Catalog Module](#6-catalog-module)
  - [6.1. Purpose](#61-purpose)
  - [6.2. Operations](#62-operations)
  - [6.3. Database Backends](#63-database-backends)
  - [6.4. Hybrid Storage Routing](#64-hybrid-storage-routing)
  - [6.5. Catalog-Indexer Contract](#65-catalog-indexer-contract)
  - [6.6. Invariants](#66-invariants)
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
- [23. Composition Rules](#23-composition-rules)
- [24. Future Considerations](#24-future-considerations)

---

<a id="1-document-information"></a>
## 1. Document Information

<a id="11-purpose-and-audience"></a>
### 1.1. Purpose and Audience

This document is the authoritative technical specification for `metadexer`, a content-addressed asset management system that handles storage, cataloging, deduplication, and search across large, heterogeneous collections of digital data.

The specification is written for an **AI-first, Human-second** audience. Its primary consumers are AI implementation agents operating within isolated context windows during sprint-based development. Every section provides sufficient detail for an AI agent to produce correct design decisions without requiring interactive clarification. Human developers and maintainers are the secondary audience.

This specification describes:

- The architectural decomposition of metadexer into its three internal modules (vault, catalog, sync) and their relationship to the external `shruggie-indexer` dependency.
- The behavioral contracts, invariants, and responsibility boundaries for each module.
- The repository structure, documentation site, configuration architecture, CLI design, and operational modes.
- The platform portability, security, and performance constraints that govern all implementation work.
- The development phasing that governs implementation ordering.

This specification does NOT serve as a user guide, tutorial, or API reference. Those artifacts are separate deliverables.

<a id="12-scope"></a>
### 1.2. Scope

<a id="in-scope"></a>
#### In Scope

- **Vault module.** Content-addressed byte storage with local filesystem and S3-compatible backends. Put, get, head, verify, and prune operations.
- **Catalog module.** Metadata registry and search engine. IndexEntry ingestion, field projection, basic and full-text search, hybrid storage routing, reference tracking, and temporal correlation. PostgreSQL and SQLite backends.
- **Sync module.** Ingestion pipeline orchestration. Sync Plan generation, deduplication, storage routing, resumable uploads, and idempotent catalog commits.
- **CLI interface.** The canonical user interface for all operations, built on `click`.
- **Configuration system.** Layered TOML configuration with compiled defaults, user config, project-local config, and CLI overrides.
- **Documentation site.** MkDocs-based documentation with the Material for MkDocs theme, deployed via GitHub Pages.
- **Packaging and distribution.** PyInstaller-based standalone executables distributed via GitHub Releases.

<a id="out-of-scope"></a>
#### Out of Scope

- **shruggie-indexer internals.** The indexer has its own specification (`shruggie-indexer-spec.md`). metadexer consumes the IndexEntry contract; it does not define or extend it.
- **Web UI.** A browser-based interface for search and browsing is a future extension ([§24](#24-future-considerations)), not part of the core specification.
- **hotwire integration.** Automated real-time feed ingestion via the hotwire pipeline is a future extension.
- **Embedding and vector search.** Semantic retrieval via vector similarity is a future extension layered on top of the catalog.

<a id="13-document-maintenance"></a>
### 1.3. Document Maintenance

This specification is maintained as a living document alongside the codebase. When the specification and the implementation disagree, the specification is presumed correct unless a deliberate amendment has been recorded in the document history.

<a id="14-conventions-used-in-this-document"></a>
### 1.4. Conventions Used in This Document

This specification uses the requirement level keywords defined in RFC 2119. These keywords are capitalized when used in their RFC 2119 sense:

| Keyword | Meaning |
|---------|---------|
| **MUST** / **MUST NOT** | Absolute requirement or prohibition. |
| **SHALL** / **SHALL NOT** | Synonymous with MUST / MUST NOT. |
| **SHOULD** / **SHOULD NOT** | Strong recommendation. Deviation must be deliberate. |
| **MAY** | Truly optional. |

Typographic conventions:

- `Monospace` denotes code identifiers, file paths, CLI flags, configuration keys, and literal values.
- **Bold** denotes emphasis or key terms being defined.
- *Italic* denotes document titles, variable placeholders, or first use of a defined term.
- `§N.N` denotes a cross-reference to a section within this specification.

Code examples use Python syntax unless otherwise noted. Examples are illustrative; they demonstrate intent and structure but are not necessarily the exact implementation.

<a id="15-terminology"></a>
### 1.5. Terminology

| Term | Definition |
|------|------------|
| **IndexEntry** | A structured JSON record produced by shruggie-indexer that serves as the authoritative metadata description of a content object. Defined by the v2 schema. |
| **Content-addressed** | An identity model where objects are identified by a hash of their byte content, not by filename or path. |
| **Vault** | The metadexer module responsible for raw byte storage under deterministic, content-derived keys. |
| **Catalog** | The metadexer module responsible for metadata storage, indexing, search, and reference tracking. |
| **Sync** | The metadexer module responsible for orchestrating the ingestion pipeline across the indexer, vault, and catalog. |
| **Sync Plan** | A dry-run preview of pending operations generated by the sync module before committing any changes. |
| **Storage routing** | The rule-based decision process that determines whether ingested content is stored inline in the catalog database or routed to the vault as binary blob storage. |
| **Sidecar file** | An external metadata file that lives alongside the file it describes, identified by filename pattern matching (e.g., `video.mp4` may have a sidecar `video.srt`). Sidecar discovery and parsing is handled by shruggie-indexer. |
| **Reference** | A mutable pointer (collection, project, tenant, snapshot) that links to an immutable asset in the catalog. |
| **Prune** | The explicit operation that removes unreferenced objects from the vault. Never triggered automatically. |
| **`storage_name`** | The deterministic filename derived from an item's `id` and extension, produced by shruggie-indexer. Used as the vault storage key. |

<a id="16-reference-documents"></a>
### 1.6. Reference Documents

| Document | Location | Description |
|----------|----------|-------------|
| metadexer Overview | `.archive/20260305-004-metadexer-overview.md` | High-level project overview covering vision, architecture, use cases, and development roadmap. This specification supersedes the overview for all technical details. |
| shruggie-indexer Spec | `shruggie-indexer` repository: `shruggie-indexer-spec.md` | The authoritative technical specification for the indexer. Defines the IndexEntry v2 schema, all indexing behavior, sidecar handling, and output contracts. |
| IndexEntry v2 Schema | [schemas.shruggie.tech/data/shruggie-indexer-v2.schema.json](https://schemas.shruggie.tech/data/shruggie-indexer-v2.schema.json) | The canonical JSON Schema definition for the v2 IndexEntry format. |

---

<a id="2-project-overview"></a>
## 2. Project Overview

<a id="21-project-identity"></a>
### 2.1. Project Identity

| Property | Value |
|----------|-------|
| Product name | metadexer |
| Organization | ShruggieTech LLC |
| Author | William Thompson |
| Language | Python 3.12+ |
| Package name | `metadexer` |
| CLI command | `metadexer` |
| Domain | metadexer.com (reserved) |

**metadexer** is the product name. It is what users install, what the CLI is called, what the documentation refers to, and what appears on metadexer.com.

**ShruggieTech** is the organizational identity (ShruggieTech LLC). It is the publisher of both shruggie-indexer and metadexer. It appears in license headers, copyright notices, and GitHub organization naming. It is not a product name.

<a id="22-relationship-to-shruggie-indexer"></a>
### 2.2. Relationship to shruggie-indexer

shruggie-indexer is a standalone tool that predates the metadexer product identity. It has its own repository, its own release schedule, its own specification, and its own branding. It is a dependency of metadexer, not a sub-component of it.

The relationship is defined by a single contract: the **IndexEntry v2 JSON schema**. shruggie-indexer produces IndexEntry records; metadexer consumes them. metadexer MUST NOT redefine IndexEntry fields or semantics. metadexer MUST NOT recompute content identity. The indexer defines truth; metadexer preserves, records, and propagates it.

shruggie-indexer v0.1.2 is the current stable release at the time of this writing. It defines identity, extracts metadata, manages sidecars, and produces well-formed IndexEntry v2 JSON.

<a id="23-design-goals"></a>
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

<a id="24-non-goals"></a>
### 2.4. Non-Goals

metadexer is explicitly not:

- A traditional Digital Asset Management system optimized for marketing workflows and approval pipelines.
- A web-first application that requires a browser for core functionality.
- A SaaS product with per-seat licensing.
- A general-purpose object storage layer (MinIO, raw S3 already do this).
- A tool that makes autonomous decisions about user data.

<a id="25-platform-and-runtime-requirements"></a>
### 2.5. Platform and Runtime Requirements

| Requirement | Value |
|-------------|-------|
| Python version | 3.12+ (enables `tomllib`, modern type hints) |
| Target platforms | Windows (x64), Linux (x64), macOS (arm64) |
| External binary dependencies | `exiftool` (required by shruggie-indexer, not directly by metadexer) |
| Configuration format | TOML (parsed by `tomllib`) |
| JSON serializer | `orjson` preferred, `json` stdlib as silent fallback |

---

<a id="3-architecture"></a>
## 3. Architecture

<a id="31-component-map"></a>
### 3.1. Component Map

```
shruggie-indexer (standalone tool, own repository)
    │
    │  produces IndexEntry v2 JSON
    │
    ▼
metadexer (single application, single repository)
    ├── vault module    - content-addressed byte storage
    ├── catalog module  - metadata registry, search, references
    └── sync module     - ingestion pipeline orchestration
```

The indexer is a standalone tool because it genuinely is one. It operates on local files, produces JSON output, has no dependency on metadexer, and is useful on its own. People use it independently to index files, generate metadata, and pipe the output into their own scripts.

The vault, catalog, and sync modules share the IndexEntry contract, share configuration, share a data lifecycle, and are invoked together in normal operation. They live in a single repository as internal modules of the metadexer application. Each module maintains a clean responsibility boundary (the vault module does not know about catalog references; the catalog module does not store raw bytes), but they are not separate projects.

<a id="32-module-responsibilities"></a>
### 3.2. Module Responsibilities

| Concern | Owner |
|---------|-------|
| Identity generation and metadata extraction | shruggie-indexer |
| Raw byte storage | metadexer vault module |
| Structured metadata, references, and search | metadexer catalog module |
| Pipeline orchestration | metadexer sync module |

No module is permitted to silently absorb a neighbor's responsibility.

<a id="33-data-flow"></a>
### 3.3. Data Flow

The standard ingestion pipeline follows this sequence:

1. The sync module accepts a directory or file target as input.
2. The sync module invokes shruggie-indexer to produce IndexEntry records for each target.
3. For each IndexEntry, the sync module checks the catalog and vault for already-present assets. Duplicates are skipped.
4. Storage routing rules examine the IndexEntry. Small text-based content is routed to inline catalog storage. Large or binary content is routed to the vault.
5. Bytes are uploaded to the vault (for vault-routed content).
6. The IndexEntry is committed to the catalog only after upload is confirmed complete.

<a id="34-operational-modes"></a>
### 3.4. Operational Modes

**Local mode.** Indexer, local vault, local catalog. No server required. Suitable for offline archival and single-user workflows.

**Remote mode.** The client invokes the indexer and computes identity locally. The client uploads bytes to a remote vault. The client commits metadata to a remote catalog. The server MAY verify integrity asynchronously by policy.

In both modes, identity always originates from the client. The sync module never delegates identity decisions to a server.

---

<a id="4-the-indexentry-contract"></a>
## 4. The IndexEntry Contract

<a id="41-ownership-and-authority"></a>
### 4.1. Ownership and Authority

The IndexEntry v2 JSON schema is defined and owned by shruggie-indexer. metadexer consumes it as a fixed contract. The authoritative behavioral specification for IndexEntry fields, types, and semantics lives in the shruggie-indexer specification (`shruggie-indexer-spec.md`, §5). This document does not duplicate that content.

metadexer MUST NOT redefine IndexEntry fields or their semantics. metadexer MUST NOT add fields to, remove fields from, or structurally alter an IndexEntry record after it is produced by the indexer. An IndexEntry received by metadexer is treated as an immutable artifact.

<a id="42-schema-location"></a>
### 4.2. Schema Location

The authoritative machine-readable schema is hosted at:

```
https://schemas.shruggie.tech/data/shruggie-indexer-v2.schema.json
```

This document uses JSON Schema Draft-07. A local copy is committed to the indexer repository at `docs/schema/shruggie-indexer-v2.schema.json`.

<a id="43-schema-evolution-rules"></a>
### 4.3. Schema Evolution Rules

These rules are owned by the shruggie-indexer specification and summarized here for metadexer implementers:

- **Additive fields are non-breaking.** New optional fields MAY be added to v2 without incrementing `schema_version`. Consumers MUST tolerate unknown optional fields.
- **Structural changes require a version bump.** Renaming, retyping, removing a required field, or altering semantic meaning constitutes a breaking change and MUST increment `schema_version`.
- **Deprecation before removal.** A field marked deprecated in version N is emitted but ignored, then removed in version N+1.
- **Consumers dispatch on `schema_version`.** The integer value `2` is checked before parsing. Documents with unrecognized versions SHOULD be rejected.

<a id="44-consumer-obligations"></a>
### 4.4. Consumer Obligations

metadexer, as an IndexEntry consumer, MUST:

- Validate `schema_version` before processing.
- Tolerate unknown optional fields without error.
- Reject records with unrecognized `schema_version` values.
- Never recompute identity fields (`id`, `storage_name`, `hashes`) unless performing an explicit integrity verification.
- Never rewrite or amend an IndexEntry outside of the indexer's own operation.

---

<a id="5-vault-module"></a>
## 5. Vault Module

<a id="51-purpose"></a>
### 5.1. Purpose

The vault module provides content-addressed byte storage. It preserves raw file content under deterministic keys derived from the IndexEntry's `storage_name` field. The vault is responsible for bytes, not metadata.

<a id="52-operations"></a>
### 5.2. Operations

| Operation | Description |
|-----------|-------------|
| **put** | Store bytes under the `storage_name` key. Write-once: if the key already exists with identical content, the operation is a no-op. If the key exists with different content, this is a hash collision and MUST be surfaced as an error. |
| **get** | Retrieve bytes by `id` or `storage_name`. |
| **head** | Check existence of an object without retrieving its bytes. |
| **verify** | Re-hash stored bytes and compare against a provided IndexEntry. Verification is always explicit, never triggered automatically during ingest. |
| **prune** | Remove unreferenced objects. Pruning is always explicit, never triggered automatically. Requires reconciliation against the catalog to determine which objects are unreferenced. |

<a id="53-storage-backends"></a>
### 5.3. Storage Backends

**Local filesystem.** The primary backend for local-mode operation. Objects are stored as files in a content-addressed directory structure under a configurable vault root path.

**S3-compatible object storage.** For remote or hybrid deployments. Compatible with AWS S3, MinIO, MEGA S4, and any S3-compatible API. Objects are stored as keys in a configured bucket using the `storage_name` as the object key.

The local backend is the first implementation target. The S3 backend is the second.

<a id="54-invariants"></a>
### 5.4. Invariants

- The same `storage_name` always maps to identical bytes (write-once guarantee).
- The vault enforces identity; it does not compute it.
- Verification is always explicit, never triggered automatically during ingest.
- Pruning is always explicit. The vault never autonomously deletes content.
- The vault module has no knowledge of catalog references, collections, or search. It stores and retrieves bytes.

<a id="55-verification-modes"></a>
### 5.5. Verification Modes

| Mode | Description |
|------|-------------|
| **Strict** | Re-hash the entire stored object and compare against the IndexEntry. |
| **Sampled** | Probabilistic audits across a fraction of stored objects. |
| **Tiered** | Frequency and depth determined by policy or asset risk classification. |

Verification is invoked by policy or on-demand. It is not part of the ingest critical path. This preserves ingestion performance while maintaining the ability to audit integrity continuously.

---

<a id="6-catalog-module"></a>
## 6. Catalog Module

<a id="61-purpose"></a>
### 6.1. Purpose

The catalog module is the metadata registry and search engine. It records and indexes everything metadexer knows about every object. It stores IndexEntry records, projects searchable fields, tracks logical references, provides query capability, and maintains the temporal history of observed objects.

<a id="62-operations"></a>
### 6.2. Operations

| Operation | Description |
|-----------|-------------|
| **ingest** | Accept an IndexEntry record and store it. Project and index searchable fields. Duplicate ingest (same `id`) is idempotent. |
| **search** | Query indexed fields including MIME type, size, timestamps, name, extension, and (for string-stored content) full-text search over content bodies. |
| **reference** | Create, list, and remove logical references (collections, projects, tenants, snapshots) that point to cataloged assets. |
| **correlate** | Link IndexEntry snapshots across time using `id`, `session_id`, and `indexed_at` to build identity evolution history. |
| **reconcile** | Compare catalog contents against the vault to detect missing or orphaned blobs. |

<a id="63-database-backends"></a>
### 6.3. Database Backends

**PostgreSQL** is the primary backend. It is built for power users running serious workloads: millions of objects, full-text search across years of ingested data, persistent infrastructure on a home server or dedicated machine. It is the default for anyone who takes their data seriously.

**SQLite** is a lightweight alternative for quick evaluation, portable single-file deployments, and casual use. It is fully functional but not optimized for the concurrent access patterns or query complexity that arise at scale.

<a id="64-hybrid-storage-routing"></a>
### 6.4. Hybrid Storage Routing

The catalog implements hybrid storage routing. Small text-based content (e.g., a 500-byte JSON response from an API feed) is stored inline as string data within the catalog database for instant full-text search. Large or binary content (e.g., a 4 GB video file) is routed to the vault. Both types are tracked by the same catalog with the same identity model.

Storage routing is determined by configurable rulesets and by explicit user direction at ingestion time. The rulesets consider factors including file size, MIME type, and content characteristics. The exact threshold and rule configuration is defined in the configuration system ([§13](#13-configuration)).

<a id="65-catalog-indexer-contract"></a>
### 6.5. Catalog-Indexer Contract

The IndexEntry is a point-in-time snapshot. Its fields describe a file's identity, metadata, and filesystem state at the moment of indexing. Over time, content hashes change when content is modified, timestamps shift through normal filesystem operations, metadata evolves as external tools and source files change, and relative paths change when files are moved or index roots differ between runs.

This transient nature is correct by design. The indexer produces accurate snapshots. The catalog receives them, correlates them across time, and maintains a durable record of identity evolution.

<a id="66-invariants"></a>
### 6.6. Invariants

- `id` is globally unique per content object. Duplicate ingest is idempotent.
- Multiple references MAY point to a single asset. Assets do not belong to references.
- Reference deletion removes the reference, not the underlying asset.
- Physical deletion from the vault requires a separate, explicit prune operation.
- The catalog does not store raw bytes (except inline string content per hybrid routing rules).

---

<a id="7-sync-module"></a>
## 7. Sync Module

<a id="71-purpose"></a>
### 7.1. Purpose

The sync module is the ingestion pipeline orchestrator. It connects the indexer, vault, and catalog into a reliable, resumable workflow. It is the primary interface through which data enters the metadexer system.

<a id="72-pipeline-stages"></a>
### 7.2. Pipeline Stages

1. Accept directory or file targets as input.
2. Invoke shruggie-indexer to produce IndexEntry records for each target.
3. Check the catalog and vault for already-present assets to avoid redundant work.
4. Apply storage routing rules to determine destination (vault or inline catalog storage).
5. Upload bytes to the vault for vault-routed content.
6. Commit IndexEntry records to the catalog only after upload is confirmed complete.

The sync module supports dry-run mode, in which it executes stages 1 through 4 and produces a Sync Plan ([§7.3](#73-sync-plans)) without committing any changes.

<a id="73-sync-plans"></a>
### 7.3. Sync Plans

A Sync Plan is a dry-run preview of pending operations. It is generated before any data is written and describes exactly what the sync module intends to do: which objects are new, which are duplicates that will be skipped, which will be routed to the vault, and which will be stored inline in the catalog. The Sync Plan is the user's opportunity to review and approve before committing.

<a id="74-invariants"></a>
### 7.4. Invariants

- Identity always originates from the client. Sync never delegates identity decisions to a server.
- Upload is confirmed complete before catalog commit.
- Catalog commit is idempotent. Resubmitting the same IndexEntry is safe.
- Sync is restartable at any point without risk of corruption or data loss.
- No asset is silently overwritten or deleted.
- Resumable operation across interrupted runs. An interrupted sync resumes from the point of interruption, not from the beginning.

---

<a id="8-reference-and-deletion-model"></a>
## 8. Reference and Deletion Model

<a id="81-asset-immutability"></a>
### 8.1. Asset Immutability

Assets are **immutable**. Once bytes are stored in the vault and an IndexEntry is committed to the catalog, the content object is fixed. References are **mutable**. Collections, projects, tenants, and snapshots are pointers that can be created, updated, and removed without affecting the underlying asset.

<a id="82-two-phase-deletion"></a>
### 8.2. Two-Phase Deletion

Deletion is always two-phase:

1. Remove references in the catalog.
2. Explicitly invoke vault prune to remove unreferenced objects.

This model prevents accidental data loss. No content is ever removed in a single implicit operation. Both phases require explicit user action.

---

<a id="9-failure-model"></a>
## 9. Failure Model

<a id="91-tolerated-failure-modes"></a>
### 9.1. Tolerated Failure Modes

metadexer MUST tolerate and recover from:

- Interrupted or partial uploads.
- Duplicate catalog commits.
- Partial batch failures (some objects in a batch succeed, others fail).
- Network failures at any stage of remote-mode operation.
- Temporary unavailability of either the catalog database or vault storage.

<a id="92-recovery-principles"></a>
### 9.2. Recovery Principles

- **Consistency over convenience.** Incomplete operations leave the system in a known, recoverable state.
- **Explicit reconciliation over implicit repair.** The system surfaces discrepancies and requires deliberate action to resolve them.

---

<a id="10-repository-structure"></a>
## 10. Repository Structure

<a id="101-top-level-layout"></a>
### 10.1. Top-Level Layout

```
metadexer/
├── .archive/
├── .github/workflows/
├── docs/
├── scripts/
├── src/metadexer/
├── tests/
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── mkdocs.yml
├── pyproject.toml
├── README.md
└── metadexer-spec.md
```

The `.archive/` directory follows the standard ShruggieTech naming convention: `<YYYYmmdd>-<ZZZ>-<title>.<ext>`, where `ZZZ` is a three-digit zero-padded increment that resets to `001` on each new date.

<a id="102-source-package-layout"></a>
### 10.2. Source Package Layout

```
src/metadexer/
├── __init__.py
├── _version.py
├── cli.py
├── vault/
│   ├── __init__.py
│   ├── store.py              # core put/get/head/verify logic
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

<a id="103-documentation-artifacts"></a>
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
| `index.md` | Documentation site landing page. Provides a project overview, quick-links section, and navigational entry points. Rendered as the site home page by MkDocs. |
| `changelog.md` | Auto-copied from `CHANGELOG.md` at the repository root. Contains a header comment identifying it as a generated file. See [§11.3](#113-changelog-synchronization). |
| `assets/images/` | Static image assets used by the documentation site (social previews, screenshots). |
| `getting-started/` | Onboarding documentation: installation guide and quick-start tutorial. |
| `user-guide/` | End-user documentation: CLI reference, configuration reference, and platform notes. Pages are populated incrementally as features stabilize. |

This layout is intentionally minimal at the DRAFT stage. Additional sections (e.g., schema reference, API documentation) are added as the corresponding features are implemented.

<a id="104-scripts-and-build-tooling"></a>
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

<a id="11-documentation-site"></a>
## 11. Documentation Site

The project documentation is published as a static site built with [MkDocs](https://www.mkdocs.org/) using the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. This matches the toolchain established by shruggie-indexer.

<a id="111-site-configuration"></a>
### 11.1. Site Configuration

The site is configured by `mkdocs.yml` at the repository root. Key configuration settings:

| Setting | Value | Purpose |
|---------|-------|---------|
| `site_name` | `metadexer` | Displayed in the site header and browser title. |
| `site_description` | Project tagline for SEO and social metadata. | |
| `site_url` | The GitHub Pages URL for the project. | Base URL for canonical links and sitemap generation. |
| `docs_dir` | `docs` | MkDocs reads all documentation source from the `docs/` directory. |
| `theme.name` | `material` | Activates the Material for MkDocs theme. |
| `theme.palette.scheme` | `slate` | Dark mode enabled by default. |
| `theme.features` | Navigation tabs, instant loading, search highlighting, content tabs. | Provides a polished, responsive documentation experience. |

Required Markdown extensions: `admonition`, `pymdownx.details`, `pymdownx.superfences`.

The `nav` key in `mkdocs.yml` defines the sidebar navigation structure explicitly rather than relying on directory auto-discovery. This ensures predictable ordering and human-readable section labels.

<a id="112-navigation-structure"></a>
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

<a id="113-changelog-synchronization"></a>
### 11.3. Changelog Synchronization

The documentation site's changelog page (`docs/changelog.md`) is a copy of `CHANGELOG.md` at the repository root. The copy is maintained manually. The file begins with a header comment identifying it as auto-copied:

```markdown
<!-- THIS FILE IS AUTO-COPIED FROM CHANGELOG.md AT THE REPOSITORY ROOT. -->
<!-- DO NOT EDIT THIS FILE DIRECTLY. Edit CHANGELOG.md instead. -->
```

The canonical changelog is `CHANGELOG.md` at the repository root. All edits are made there. When the documentation site is built or deployed, `docs/changelog.md` MUST reflect the current state of `CHANGELOG.md`. If the two files diverge, the root `CHANGELOG.md` is authoritative.

<a id="114-build-and-preview"></a>
### 11.4. Build and Preview

| Command | Purpose |
|---------|---------|
| `mkdocs serve` | Starts a local development server with live reload at `http://127.0.0.1:8000/`. |
| `mkdocs build` | Produces the static site in the `site/` directory. The `site/` directory is listed in `.gitignore` and is never committed. |

<a id="115-deployment"></a>
### 11.5. Deployment

The documentation site is deployed to GitHub Pages via a dedicated GitHub Actions workflow (`.github/workflows/docs.yml`). The workflow:

- **Triggers** on push to `main` when files in `docs/` or `mkdocs.yml` change.
- **Builds** the site using `mkdocs build --strict` (strict mode fails the build on warnings such as broken links or missing pages).
- **Deploys** the built `site/` directory to the `gh-pages` branch using `mkdocs gh-deploy --force`.

The `--strict` flag ensures that documentation quality is enforced in CI. Broken internal links, missing navigation targets, and unreferenced pages cause build failures rather than silent degradation.

<a id="116-dependencies"></a>
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

<a id="12-cli-interface"></a>
## 12. CLI Interface

<a id="121-command-structure"></a>
### 12.1. Command Structure

The CLI uses `click` as the argument parser. The top-level command is `metadexer`. Subcommands map to module operations. The exact subcommand tree is defined during implementation, but the following structure reflects the expected shape:

```
metadexer ingest <target>       # run the sync pipeline on a target directory or file
metadexer search <query>        # query the catalog
metadexer vault verify [...]    # explicit vault verification
metadexer vault prune [...]     # explicit vault pruning
metadexer catalog reconcile     # reconcile catalog against vault
metadexer config [...]          # configuration management
```

<a id="122-cli-conventions"></a>
### 12.2. CLI Conventions

- Content filtering flags are independent of output destination flags.
- `stdout` stays clean for structured output (JSON). All diagnostics go to `stderr`.
- Destructive operations require explicit opt-in flags.
- `--dry-run` mode is available for any operation with side effects.
- CLI contracts are the canonical interface. API and daemon layers are secondary and MUST NOT implement independent behavior.

---

<a id="13-configuration"></a>
## 13. Configuration

<a id="131-configuration-architecture"></a>
### 13.1. Configuration Architecture

All configuration uses **TOML** format, parsed by Python's `tomllib` module.

Layered override behavior (lowest to highest priority):

1. Compiled defaults (always present; a Python module, not a TOML file).
2. User config directory (platform-specific; see [§13.2](#132-application-data-directory)).
3. Project-local config (searched upward from target directory).
4. CLI arguments (highest priority).

Configuration objects SHOULD be frozen (immutable) dataclasses. Unknown keys in user-provided TOML MUST be silently ignored (forward compatibility). Invalid values MUST produce clear error messages naming the offending key and value.

<a id="132-application-data-directory"></a>
### 13.2. Application Data Directory

metadexer resolves its application data directory through a single canonical module. No other module MAY resolve application data paths independently.

| Platform | Base path |
|----------|-----------|
| Windows | `%LOCALAPPDATA%\shruggie-tech\metadexer\` |
| Linux | `~/.config/shruggie-tech/metadexer/` |
| macOS | `~/Library/Application Support/shruggie-tech/metadexer/` |

The `shruggie-tech` namespace is shared between shruggie-indexer and metadexer:

```
<platform_base>/shruggie-tech/
├── shared.toml                  # (future: cross-tool configuration)
├── shruggie-indexer/
│   ├── config.toml
│   ├── gui-session.json
│   └── logs/
└── metadexer/
    ├── config.toml
    └── logs/
```

On Windows, all data goes under `%LOCALAPPDATA%` (Local), not `%APPDATA%` (Roaming).

---

<a id="14-file-encoding-and-json-conventions"></a>
## 14. File Encoding and JSON Conventions

<a id="141-file-encoding-and-line-endings"></a>
### 14.1. File Encoding and Line Endings

All source files, configuration files, output files, documentation files, and specification documents MUST use:

- **UTF-8 encoding without BOM.**
- **LF (Unix) line endings.**

This is a hard invariant. Output functions MUST use `encoding="utf-8"` explicitly, never relying on platform defaults.

<a id="142-json-conventions"></a>
### 14.2. JSON Conventions

- All JSON output uses UTF-8 encoding without BOM.
- Serializers SHOULD use compact formatting for production output.
- `null` is used (not omitted) for explicitly absent values on required fields. Optional fields that are `None` are omitted from output.
- Non-ASCII characters are preserved as literal UTF-8, not escaped to `\uXXXX` sequences.
- `orjson` is preferred for performance where available, with `json.dumps()` as a silent fallback.

---

<a id="15-external-dependencies"></a>
## 15. External Dependencies

<a id="151-python-dependencies"></a>
### 15.1. Python Dependencies

The full dependency inventory is defined during implementation in `pyproject.toml`. The following are known required dependencies:

| Package | Purpose | Category |
|---------|---------|----------|
| `click` | CLI argument parsing | Required |
| `orjson` | High-performance JSON serialization | Optional (silent fallback to `json` stdlib) |
| `psycopg` (or equivalent) | PostgreSQL database driver | Required for PostgreSQL backend |
| `boto3` (or equivalent) | S3-compatible object storage client | Required for S3 backend |
| `shruggie-indexer` | IndexEntry production | Required (invoked as subprocess or library) |

<a id="152-external-service-dependencies"></a>
### 15.2. External Service Dependencies

| Service | Required | Notes |
|---------|----------|-------|
| PostgreSQL | For PostgreSQL catalog backend | Not required when using SQLite backend |
| S3-compatible storage | For S3 vault backend | Not required when using local filesystem backend |

<a id="153-dependency-verification-at-runtime"></a>
### 15.3. Dependency Verification at Runtime

| Category | Failure mode |
|----------|-------------|
| Required CLI dependency (e.g., `click`) | Hard error with install instructions. |
| Required backend dependency (e.g., `psycopg`) | Hard error when that backend is selected. |
| Optional performance dependency (e.g., `orjson`) | Silent fallback to stdlib equivalent. |
| Development/test dependency (e.g., `pytest`) | Import error at test time only. |

---

<a id="16-logging-and-diagnostics"></a>
## 16. Logging and Diagnostics

All logging uses Python's standard `logging` module. Logger names follow the package structure (e.g., `metadexer.vault.store`, `metadexer.catalog.ingest`, `metadexer.sync.pipeline`).

Log output goes to `stderr` (console) and optionally to persistent log files under `<app_data_dir>/logs/`. Log files use the naming pattern `YYYY-MM-DD_HHMMSS.log`.

---

<a id="17-testing"></a>
## 17. Testing

Test suites are organized by test type, not by source module:

| Category | Directory | Scope |
|----------|-----------|-------|
| Unit | `tests/unit/` | Individual functions and methods in isolation. |
| Integration | `tests/integration/` | Full pipeline, end-to-end. |
| Conformance | `tests/conformance/` | Output structure against canonical schemas and contracts. |
| Platform | `tests/platform/` | OS-specific behavior. |

All tests run with a bare `pytest` invocation. `pyproject.toml` registers custom markers with `--strict-markers`. Platform-specific tests use pytest markers (`@pytest.mark.platform_windows`, `@pytest.mark.platform_linux`, `@pytest.mark.platform_macos`) and are executed on the corresponding platform in CI.

---

<a id="18-packaging-and-distribution"></a>
## 18. Packaging and Distribution

metadexer is **not published to PyPI**. End users download pre-built executables from GitHub Releases.

Packaging stack:

- `pyproject.toml` as the single metadata and dependency declaration file.
- PyInstaller for standalone executables.
- GitHub Actions release pipeline triggered on `v*` tag pushes, with matrix builds for Windows (x64), Linux (x64), and macOS (arm64).

Release pipeline stages: Checkout, Test, Build (PyInstaller), Rename artifacts (version + platform tags), Upload, Create GitHub Release.

The version string lives in a single `_version.py` file. All other references derive from it. Versioning follows semantic versioning (`MAJOR.MINOR.PATCH`). Pre-release versions use suffixes like `-rc1`.

---

<a id="19-platform-portability"></a>
## 19. Platform Portability

<a id="191-cross-platform-design-principles"></a>
### 19.1. Cross-Platform Design Principles

Design goal G9 ([§2.3](#23-design-goals)) states: the application MUST run on Windows, Linux, and macOS from a single codebase. The following principles govern the approach to platform portability:

**No platform-conditional logic in the core modules.** The `vault/`, `catalog/`, and `sync/` subpackages MUST NOT contain `if sys.platform == ...` or `if os.name == ...` branches. All platform variation is absorbed by Python standard library abstractions (`pathlib`, `os`, `hashlib`, `subprocess`) or by the configuration system. The one permitted exception is the `cli.py` entry point, which MAY contain platform-conditional logic for presentation-layer concerns (console encoding, terminal setup) that do not affect application behavior.

**Forward-slash normalization in stored paths.** All path strings stored in the catalog use forward-slash (`/`) separators, regardless of the host platform. This ensures that catalog data is portable across operating systems.

**Graceful degradation for unavailable features.** When a platform does not support a feature, the application uses the best available approximation and logs a debug-level message on first occurrence. No per-file warnings are produced for known platform limitations.

<a id="192-platform-specific-considerations"></a>
### 19.2. Platform-Specific Considerations

**Windows.** The application data directory resolves under `%LOCALAPPDATA%` (Local), not `%APPDATA%` (Roaming). Long path support (`\\?\` prefix) is handled by Python's `pathlib` where applicable. Console output encoding is set to UTF-8 explicitly.

**Linux.** The application data directory follows the XDG Base Directory Specification, defaulting to `~/.config/` when `XDG_CONFIG_HOME` is not set.

**macOS.** The application data directory resolves to `~/Library/Application Support/`. The arm64 architecture is the primary macOS build target.

Platform-specific behaviors are verified by the `tests/platform/` test suite ([§17](#17-testing)).

---

<a id="20-security-and-safety"></a>
## 20. Security and Safety

<a id="201-path-validation-and-sanitization"></a>
### 20.1. Path Validation and Sanitization

All user-supplied path inputs MUST be resolved to canonical absolute paths before use. The application MUST NOT follow symbolic links into directories outside the user-specified target scope unless explicitly directed. Path traversal attacks (e.g., `../../etc/passwd` embedded in filenames or metadata) MUST be detected and rejected.

Vault storage keys are derived from `storage_name` values produced by the indexer (deterministic, content-derived, alphanumeric with a single dot separator). The vault backend MUST validate that storage keys conform to the expected pattern before performing any filesystem or object storage operation.

<a id="202-destructive-operation-safeguards"></a>
### 20.2. Destructive Operation Safeguards

All destructive operations require explicit opt-in flags. This applies to vault prune, reference deletion, catalog entry removal, and any operation that modifies or removes stored data. No destructive action is ever a default. `--dry-run` mode is available for any operation with side effects, and `--dry-run` MUST be the default behavior for prune operations unless an explicit confirmation flag is provided.

<a id="203-credential-and-secret-handling"></a>
### 20.3. Credential and Secret Handling

Database connection strings, S3 access keys, and other credentials MUST NOT be stored in plaintext configuration files. Credentials are supplied via environment variables or platform-native credential storage mechanisms. Configuration files MAY reference environment variable names but MUST NOT contain credential values directly. Credentials MUST NOT appear in log output at any log level.

<a id="204-large-file-and-resource-limit-handling"></a>
### 20.4. Large File and Resource Limit Handling

The vault module handles files of arbitrary size. File content MUST be read and written in chunks (not loaded entirely into memory) to prevent memory exhaustion on large objects. Hash computation during verification MUST use streaming (chunked) reads. The catalog module MUST handle IndexEntry records of arbitrary depth (deeply nested directory trees with large `items` arrays) without stack overflow. Configurable limits on batch sizes and concurrent operations prevent resource exhaustion during bulk ingestion.

---

<a id="21-performance-considerations"></a>
## 21. Performance Considerations

<a id="211-ingestion-pipeline-performance"></a>
### 21.1. Ingestion Pipeline Performance

The ingestion pipeline is designed for throughput at scale (millions of files, terabytes of data). Deduplication checks against the catalog and vault MUST be performed before any byte transfer to avoid redundant I/O. Batch operations (catalog commits, vault existence checks) SHOULD be used where the backend supports them to minimize round-trip overhead.

<a id="212-catalog-query-performance"></a>
### 21.2. Catalog Query Performance

The catalog schema MUST include appropriate indexes on commonly queried fields: `id`, `mime_type`, `size.bytes`, `timestamps.modified`, `name.text`, and `extension`. Full-text search over string-stored content uses the database engine's native full-text search capabilities (PostgreSQL `tsvector`/`tsquery`, SQLite FTS5). Index design is documented as part of the catalog backend implementation.

<a id="213-vault-io-performance"></a>
### 21.3. Vault I/O Performance

Vault operations use chunked I/O for all file reads and writes. The chunk size is configurable with a sensible default (e.g., 8 MB). For the S3 backend, multipart upload is used for objects exceeding the S3 single-upload size threshold. The local filesystem backend uses a directory sharding strategy (e.g., first N characters of `storage_name` as subdirectory prefixes) to prevent performance degradation from directories with millions of entries.

---

<a id="22-development-phases"></a>
## 22. Development Phases

Phase 1 (Foundation) is complete: shruggie-indexer v0.1.2 is released and stable. The following phases define the remaining implementation ordering.

<a id="221-phase-2-storage-and-catalog"></a>
### 22.1. Phase 2: Storage and Catalog

**Target:** A working local-mode system where `metadexer ingest <directory>` indexes files, stores bytes in a local vault, and commits metadata to a catalog with basic query support.

Scope:

- Vault module: put, get, head, verify. Local filesystem backend first. S3-compatible backend second.
- Catalog module: IndexEntry ingest, field projection, basic search (MIME type, size, timestamps, name, extension). PostgreSQL backend as primary target. SQLite backend for portable/evaluation use. Hybrid string storage for small text-based content.

Deferred from this phase: reference tracking (collections/projects/users), temporal correlation, reconciliation, pruning.

<a id="222-phase-3-pipeline"></a>
### 22.2. Phase 3: Pipeline

**Target:** A reliable, resumable ingestion pipeline with dry-run support.

Scope:

- Sync Plan generation (dry-run preview of pending operations).
- Deduplication checks against existing catalog/vault state.
- Storage routing based on configurable rulesets.
- Resumable operation across interrupted runs.
- Idempotent catalog commits.

<a id="223-phase-4-search-and-scale"></a>
### 22.3. Phase 4: Search and Scale

**Target:** Full catalog capabilities as specified in [§6](#6-catalog-module).

Scope:

- Full-text search over string-stored content.
- Reference tracking (collections, projects, tenants).
- Temporal correlation of IndexEntry snapshots.
- Vault reconciliation (detect orphaned or missing blobs).
- Vault pruning for unreferenced objects.

<a id="224-phase-5-integration-and-polish"></a>
### 22.4. Phase 5: Integration and Polish

Scope:

- hotwire integration (automated feed ingestion pipeline).
- Web UI for search and browsing (thin layer over API).
- MEGA S4 as a vault backend.
- Documentation site, public release, metadexer.com.

---

<a id="23-composition-rules"></a>
## 23. Composition Rules

No module MAY:

- Recompute identity unless performing an explicit integrity verification.
- Rewrite or amend an IndexEntry outside of the indexer's own operation.
- Implicitly delete content from any backend.
- Implicitly migrate content between backends.

Cross-module interaction within metadexer occurs through defined internal APIs. The indexer communicates with metadexer exclusively through the IndexEntry JSON contract.

---

<a id="24-future-considerations"></a>
## 24. Future Considerations

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
| 2026-03-07 | DRAFT | Initial specification. Derived from the metadexer high-level overview (`20260305-004-metadexer-overview.md`). Establishes architectural contracts, module responsibilities, invariants, and development phasing sufficient for sprint planning. |
