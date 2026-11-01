# CONN-CLARITY-API-DATA-PLATFORM-OPERATIONS — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The operation joins the existing tool surface in `clarity_api/mcp/mcp_insights.py`. It reuses the connector's client and auth. One tool per API operation. Read-only. The connector returns typed data; medulla maps it.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 1 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
clarity_api/mcp/mcp_insights.py  existing
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

### Interfaces and data model

A new MCP tool with a typed result. No migration.

### Live integration path

Client call, then the MCP tool in `clarity_api/mcp/mcp_insights.py`, then the backend API.

### Quality and release gates

The repo's pre-commit gates and the focused test named in the row.

### Risks, alternatives, and decisions

A backend without the capability returns a typed unsupported result.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `ruff-format`, `connector-standard`, `secrets`, `tests-fast`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

Each row's `Caller chain:` sentence in [requirements.md](requirements.md) traces the entry point to the code.

## Cross-repo seams

none. The cited owner rows are library capabilities the connector calls in process; spec.md names them.
