# CONN-CLARITY-API-CONNECTOR-CONTENT — The connector serves its packaged content

Owner: clarity-api. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R071`, `SCION-CONNECTOR-CONTROL-R073`.

## Purpose and user stories

The `clarity-mcp` server serves its packaged skills, prompts and ontology to any client, with no wiring of its own.

## Why a new spec

The specs of this repository were read; none owns this capability. This spec states it for this connector only.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - The connector serves its packaged content (Priority: P1)

The `clarity-mcp` server serves its packaged skills, prompts and ontology to any client, with no wiring of its own.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-CLARITY-API-CONNECTOR-CONTENT-R001` (default content) is exercised, **Then** `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-CLARITY-API-CONNECTOR-CONTENT-R002` (declare access contracts for the competency reads of clarity-api) is exercised, **Then** declare access contracts for the competency reads of clarity-api.

### Edge Cases

- If `CONN-CLARITY-API-CONNECTOR-CONTENT-R001` is not met, its proving test fails: default content.
- If `CONN-CLARITY-API-CONNECTOR-CONTENT-R002` is not met, its proving test fails: declare access contracts for the competency reads of clarity-api.

## Requirements

- **FR-001**: Default content. Rows: `CONN-CLARITY-API-CONNECTOR-CONTENT-R001`.
- **FR-002**: Declare access contracts for the competency reads of clarity-api. Rows: `CONN-CLARITY-API-CONNECTOR-CONTENT-R002`.

## Success Criteria

- **SC-001**: `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt. Rows: `CONN-CLARITY-API-CONNECTOR-CONTENT-R001`.
- **SC-002**: Declare access contracts for the competency reads of clarity-api. Rows: `CONN-CLARITY-API-CONNECTOR-CONTENT-R002`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-CLARITY-API-CONNECTOR-CONTENT-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-CLARITY-API-CONNECTOR-CONTENT-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
