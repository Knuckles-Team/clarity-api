# Concept Registry — clarity-api

> **Prefix**: `CONCEPT:CLA-*`
> **Version**: 1.0.0
> **Bridge**: [ECO-4.0](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/concepts.md) (Unified Toolkit Ingestion)

---

## Project-Specific Concepts

Each concept below is traced bidirectionally across **code** (a `CONCEPT:CLA-*`
docstring marker on the implementing function), **docs** (this registry), and
**tests** (a `@pytest.mark.concept("CLA-00X")` marker on the exercising test).

| Concept ID | Name | Implementation | Test |
|------------|------|----------------|------|
| `CONCEPT:CY-OS.governance.data-export-live-insights` | Data Export / Live Insights | `clarity_insights` MCP tool + `ClarityApiInsights.get_data_export` (`/export-data/api/v1/project-live-insights`) | `test_concept_cla_001_*` |
| `CONCEPT:CY-OS.identity.credential-auth-factory-supports` | Credential & Auth Factory | `clarity_api.auth.get_client` — OIDC delegation (RFC 8693) / fixed-token resolution | `test_concept_cla_002_*` |
| `CONCEPT:CY-OS.governance.input-validation-parameter-modeling` | Input Validation & Parameter Modeling | `clarity_api.clarity_models.InputModel` — date-range + dimension validation | `test_concept_cla_003_*` |
| `CONCEPT:CY-OS.governance.rest-base-client-owns` | REST Base Client | `clarity_api.api.api_client_base.ClarityApiBase` — session, bearer auth, fail-fast credential validation | `test_concept_cla_004_*` |
| `CONCEPT:CY-OS.governance.package-server-bootstrap` | Package & Server Bootstrap | `clarity_api.__init__` lazy loading, `mcp_server.mcp_server`, `agent_server.agent_server` entry points | `test_concept_cla_005_*` |
| `CONCEPT:CY-OS.governance.cla` | Concept Traceability Governance | `tests/unit/test_concept_parity.py` parity gates: every `CLA-*` tag is documented and every inherited pillar concept is registered upstream | `test_concept_cla_006_*` |

## Cross-Project References (from agent-utilities)

> These are inherited platform capabilities from `agent-utilities`. They are
> **not** clarity-api project concepts and are listed here for traceability only
> (rendered as plain IDs so they are not counted as orphaned project concepts).

| Concept ID | Name | Origin |
|------------|------|--------|
| ECO-4.0 | Unified Toolkit Ingestion | agent-utilities |
| ORCH-1.2 | Confidence-Gated Router | agent-utilities |
| OS-5.1 | Prompt Injection Defense | agent-utilities |
| OS-5.2 | Cognitive Scheduler | agent-utilities |
| AU-OS.governance.reactive-multi-axis-budget | Guardrail Engine | agent-utilities |
| AU-OS.governance.wasm-micro-agent-sandbox | Audit Logging | agent-utilities |
| KG-2.0 | Knowledge Graph Core | agent-utilities |

## Synergy with agent-utilities

This project integrates with `agent-utilities` via the ECO-4.0 (Unified Toolkit
Ingestion) bridge. The `clarity_api` MCP server registers its tools with the
agent-utilities FastMCP middleware, enabling automatic discovery, telemetry, and
Knowledge Graph ingestion of all `CLA-*` concepts.
