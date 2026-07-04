---
name: clarity-analytics-ingestion
description: >-
  Natively ingest a Microsoft Clarity behavioral-analytics export into the
  epistemic-graph knowledge graph via the clarity-api MCP server — pushing typed
  :ClarityProject / :ClaritySession / :BehaviorInsight / :BehaviorDimension nodes
  plus a :Document summary with their :belongsToProject / :hasInsight /
  :brokenDownBy links. Use when the agent must persist Clarity metrics into the KG
  for cross-source reasoning or semantic search. Do NOT use to merely read/return
  metrics (use clarity-behavioral-insights) or for non-Clarity sources.
license: MIT
tags: [clarity, analytics, knowledge-graph, ingestion, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# Clarity Analytics Ingestion

Push a Microsoft Clarity Data Export into the ONE epistemic-graph knowledge graph
as **typed OWL nodes** via the `clarity-api` MCP server. Backed by the package's
native `kg_ingest` mapper (`CONCEPT:AU-KG.ingest.enterprise-source-extractor`) over
the shared engine-client txn write path.

## When to use
- Persist recent Clarity metrics into the KG for cross-source reasoning.
- Make behavioral data searchable via the ingested `:Document` summaries.
- Materialize `:ClaritySession` snapshots + per-metric `:BehaviorInsight` nodes for
  later graph queries.

## When NOT to use
- You only need to read/return the numbers → `clarity-behavioral-insights`.
- No KG engine is reachable — the tool then no-ops (`{"ingested": null}`); that is
  expected, not an error.
- Non-Clarity analytics sources — out of scope.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`clarity-api`** MCP server. Same
credentials as `clarity-behavioral-insights`:

| Variable | Required | Notes |
|----------|----------|-------|
| `CLARITY_URL` | optional | Instance base URL (default `https://www.clarity.ms`) |
| `CLARITY_TOKEN` | ✅ | Bearer API token |
| `CLARITY_SSL_VERIFY` | optional | TLS verification toggle |

Ingestion targets a reachable epistemic-graph engine (the fleet `graph-os`); with
none present the push is a clean no-op. Note the standard `clarity_insights`
`get_data_export` call **also** ingests best-effort as a side effect — this tool is
the explicit, Wire-First entry point.

## Tools & actions
| Tool | Purpose |
|------|---------|
| `clarity_ingest_insights` | Pull the live-insights export and push typed nodes + a summary document into the KG. |

### Key parameters (`params_json`)
Same shape as the export call: `number_of_days` (`1`|`2`|`3`) and optional
`dimension_1`/`dimension_2`/`dimension_3` (`Browser`, `Device`, `Country`, `OS`,
`Source`, `Medium`, `Campaign`, `Channel`, `URL`).

## Recipes (`params_json`)
Ingest the last 3 days, broken down by OS:
```json
{"number_of_days": 3, "dimension_1": "OS"}
```
Ingest overall totals for the last day:
```json
{"number_of_days": 1}
```

## Node & id conventions
- `:ClarityProject` → `clarity:project:<project>`
- `:ClaritySession` → `clarity:session:<project>:<days>:<dimkey>`
- `:BehaviorInsight` → `clarity:insight:<project>:<days>:<dimkey>:<metricName>`
- `:BehaviorDimension` → `clarity:dimension:<name>`
- `:Document` → `clarity:doc:<project>:<days>:<dimkey>`

## Gotchas
- Best-effort by design: `{"ingested": null}` means no engine was reachable, not a
  failure — the read still returns data.
- The `project` label is derived from the `CLARITY_URL` host (the token scopes one
  project); ids are stable per host + window + dimension key.
- Session counts are aggregated from the first count-bearing metric's rows; string
  counts are cast to integers during mapping.
- Re-ingesting the same window MERGEs onto the same node ids (idempotent), it does
  not create duplicates.

## Related
- `clarity-behavioral-insights` — read/interpret the same export without KG writes.
- The `agent-utilities-source-integration` skill covers the broader "connect a
  source to the KG" flow this tool participates in.
