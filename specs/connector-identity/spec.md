# CONN-CLARITY-API-CONNECTOR-IDENTITY — The connector is filed under its fleet name

Owner: clarity-api. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R071`, `PIPE-GATES-R010`.

## Purpose and user stories

The engine and arbora list a connector's tools and ingest under its fleet name. This connector's fleet name is `clarity-mcp`.

## Why a new spec

The specs of this repository were read; none owns this capability. This spec states it for this connector only.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - The connector is filed under its fleet name (Priority: P1)

The engine and arbora list a connector's tools and ingest under its fleet name. This connector's fleet name is `clarity-mcp`.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-CLARITY-API-CONNECTOR-IDENTITY-R001` (fleet name) is exercised, **Then** every connector name in the package is `clarity-mcp`.

### Edge Cases

- If `CONN-CLARITY-API-CONNECTOR-IDENTITY-R001` is not met, its proving test fails: fleet name.

## Requirements

- **FR-001**: Fleet name. Rows: `CONN-CLARITY-API-CONNECTOR-IDENTITY-R001`.

## Success Criteria

- **SC-001**: Every connector name in the package is `clarity-mcp`. Rows: `CONN-CLARITY-API-CONNECTOR-IDENTITY-R001`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-CLARITY-API-CONNECTOR-IDENTITY-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
