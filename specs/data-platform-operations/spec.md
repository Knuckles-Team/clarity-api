# CONN-CLARITY-API-DATA-PLATFORM-OPERATIONS — Operations the data-platform vocabulary needs

Owner: clarity-api. Cross-repo IDs: `MEDULLA-DATAPLAT-VOCAB-R009`.

## Purpose and user stories

The medulla data-platform vocabulary answers competency questions from connector facts. One question needs an operation this connector lacks. This spec owns that operation.

## Why a new spec

The existing specs in `specs/` cover packaged content and identity, not tool operations. None owns a new connector operation.

## Scope and interfaces

Owned: the one operation named in the row, touching `clarity_api/mcp/mcp_insights.py`. Non-goal: anything in the medulla vocabulary itself.

## Traceability

| Requirement | Design section | Test ID | Evidence |
|---|---|---|---|
| CONN-CLARITY-API-DATA-PLATFORM-OPERATIONS-R001 | plan.md | T-001 |  |

## Open questions

- None.

## User Scenarios & Testing

### User Story 1 - Operations the data-platform vocabulary needs (Priority: P1)

The medulla data-platform vocabulary answers competency questions from connector facts. One question needs an operation this connector lacks. This spec owns that operation.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-CLARITY-API-DATA-PLATFORM-OPERATIONS-R001` (rage-click and dead-click metrics) is exercised, **Then** fixture export returns the two metrics for the URL dimension.

### Edge Cases

- If `CONN-CLARITY-API-DATA-PLATFORM-OPERATIONS-R001` is not met, its proving test fails: rage-click and dead-click metrics.

## Requirements

- **FR-001**: Rage-click and dead-click metrics. Rows: `CONN-CLARITY-API-DATA-PLATFORM-OPERATIONS-R001`.

## Success Criteria

- **SC-001**: Fixture export returns the two metrics for the URL dimension. Rows: `CONN-CLARITY-API-DATA-PLATFORM-OPERATIONS-R001`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-CLARITY-API-DATA-PLATFORM-OPERATIONS-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
