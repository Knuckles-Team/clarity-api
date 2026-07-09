---
name: clarity-behavioral-insights
skill_type: skill
description: >-
  Export and interpret Microsoft Clarity behavioral-analytics via the clarity-api
  MCP server — pull dashboard "live insights" (sessions, bot traffic, distinct
  users, pages-per-session) over a 1-3 day window, optionally segmented by up to
  three dimensions (Browser, Device, Country, OS, Source, Medium, Campaign,
  Channel, URL). Use when the agent must read Clarity metrics, compare traffic by
  a dimension, or summarize recent behavioral trends. Do NOT use to push those
  metrics into the knowledge graph (use clarity-analytics-ingestion) or for any
  non-Clarity web analytics.
license: MIT
tags: [clarity, analytics, behavioral, web-analytics, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# Clarity Behavioral Insights

Domain-typed access to the Microsoft Clarity **Data Export / Live Insights**
endpoint (`GET /export-data/api/v1/project-live-insights`) via the `clarity-api`
MCP server. Returns per-metric rows (session counts, bot sessions, distinct
users, pages-per-session) for a trailing date window, optionally broken down by
up to three dimensions.

## When to use
- Read recent Clarity metrics for the token-scoped project.
- Compare traffic/engagement across a dimension (e.g. sessions by `OS` or
  `Country`).
- Summarize behavioral trends over the last 1, 2, or 3 days.

## When NOT to use
- Ingesting the export into the epistemic-graph knowledge graph → use
  `clarity-analytics-ingestion`.
- Windows longer than 3 days or historical backfill — the Live Insights API only
  supports `number_of_days` of 1, 2, or 3.
- Non-Clarity analytics (GA, Matomo, etc.) — out of scope.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`clarity-api`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `CLARITY_URL` | optional | Instance base URL (default `https://www.clarity.ms`) |
| `CLARITY_TOKEN` | ✅ | Bearer API token from the Clarity project settings |
| `CLARITY_SSL_VERIFY` | optional | TLS verification toggle (default `True`) |

`MCP_TOOL_MODE` (`condensed`|`verbose`|`both`) selects the condensed surface
(used below) vs. the one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tool; it takes `action` + a `params_json` **JSON string**.

| Condensed tool | Actions |
|----------------|---------|
| `clarity_insights` | `get_data_export` |

### Key parameters (`params_json`)
- `number_of_days` — `1`, `2`, or `3` (the trailing window; required for a useful call).
- `dimension_1`, `dimension_2`, `dimension_3` — optional breakdowns. Valid values:
  `Browser`, `Device`, `Country`, `OS`, `Source`, `Medium`, `Campaign`,
  `Channel`, `URL` (case-insensitive; normalized server-side).

## Recipes (`params_json`)
Last 3 days, no breakdown (overall totals):
```json
{"number_of_days": 3}
```
Sessions broken down by operating system:
```json
{"number_of_days": 3, "dimension_1": "OS"}
```
Two-dimension breakdown (device × country):
```json
{"number_of_days": 2, "dimension_1": "Device", "dimension_2": "Country"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- `number_of_days` outside `{1,2,3}` is rejected by the API's `InputModel`
  validation; there is no wider historical range on this endpoint.
- At most **three** dimensions per call; an invalid dimension name raises a
  parameter error.
- Count fields (`totalSessionCount`, `totalBotSessionCount`, `distantUserCount`)
  come back as **strings** in the row payload — cast before arithmetic.
- The token scopes exactly one project; there is no project selector on the call.

## Related
- `clarity-analytics-ingestion` — push the same export into the knowledge graph as
  typed `:ClaritySession` / `:BehaviorInsight` nodes + a `:Document` summary.
