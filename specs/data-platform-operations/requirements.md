# CONN-CLARITY-API-DATA-PLATFORM-OPERATIONS — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-CLARITY-API-DATA-PLATFORM-OPERATIONS-R001` | **Rage-click and dead-click metrics.** `get_data_export` names and surfaces both metrics by URL. Touches `clarity_api/mcp/mcp_insights.py`. Moved from `EG-DATAPLAT-VOCAB-R009.4` (medulla). | fixture export returns the two metrics for the URL dimension. |
