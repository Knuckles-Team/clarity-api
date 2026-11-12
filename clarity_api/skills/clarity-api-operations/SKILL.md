---
name: clarity-api-operations
skill_type: skill
description: >-
  Operate clarity-api through its governed MCP and Arbora capabilities, including clarity analytics ingestion, clarity behavioral insights. Use when a request requires this provider's read, change, automation, ingestion, troubleshooting, or evidence workflows.
---

# Clarity Api Operations

Use the provider's governed MCP tools through Arbora delegation.

## Workflow

1. Establish the verified GraphSession and tenant before discovery or retrieval.
2. Discover the current tool surface; never assume a stale tool name or schema.
3. Prefer read-only inspection first. For changes, present impact and use the provider's
   dry-run or preview mode when available.
4. Execute mutations as fenced WorkItems so retries remain idempotent and auditable.
5. Ingest source data only through the signed connector preset and ChangeEnvelope path.
6. Verify the durable result and its trace/evidence before reporting completion.

## Tools

| Tool | Use |
|------|-----|
| `clarity_get_data_export` | Read live insights for a 1-3 day window with up to three dimensions. |
| `clarity_ingest_insights` | Read the same export and write it to the knowledge graph as typed nodes. |

## Tasks

- Report traffic by dimension: call `clarity_get_data_export` with `number_of_days` and `dimension_1` to `dimension_3`.
- Persist an export: call `clarity_get_data_export`, then `clarity_ingest_insights` with the same arguments.

## Safety contract

- Never persist credentials, endpoints, raw personal identifiers, hostnames, or local paths.
- Resolve TLS trust and verification from environment/configuration; never hardcode bypasses.
- Treat unknown ACL, tenant, schema, or tool-contract state as a hard failure.
- Require explicit approval for destructive, externally visible, or irreversible actions.
- Keep runtime traces policy-scoped and privacy-sanitized.

## Specialized workflows

Read [the workflow catalog](references/catalog.md) only when the request needs a
provider-specific procedure, parameter map, script, or reference asset.
