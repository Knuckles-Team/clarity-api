# clarity-api — Concept Overview

> **Category**: Analytics | **Ecosystem Role**: MCP Server + A2A Agent
> Built on [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities) — the unified AGI Harness.

## Description

Microsoft Clarity API + MCP Server + A2A Server

## Enterprise Readiness

All agents in the ecosystem inherit enterprise-grade infrastructure from `agent-utilities`:

| Feature | Status | Source |
|:--------|:-------|:-------|
| **JWT/OIDC Authentication** | ✅ Built-in | `agent-utilities[auth]` — Authlib JWKS + API key middleware |
| **OpenTelemetry Instrumentation** | ✅ Built-in | `agent-utilities[logfire]` — OTLP export, FastAPI auto-instrumentation |
| **HashiCorp Vault Integration** | ✅ Built-in | `agent-utilities[vault]` — `secret://`, `env://`, `vault://` URI schemes |
| **Audit Logging** | ✅ Built-in | Append-only compliance trail with 30+ action types (agent-utilities AU-OS.governance.wasm-micro-agent-sandbox) |
| **Token Usage Analytics** | ✅ Built-in | 4-bucket tracking with budget alerting (agent-utilities AU-OS.governance.wasm-micro-agent-sandbox) |
| **Prompt Injection Defense** | ✅ Built-in | 25+ pattern scanner + jailbreak taxonomy (agent-utilities OS-5.1) |
| **Guardrail Engine** | ✅ Built-in | Input/output interception with block/redact/warn (agent-utilities AU-OS.governance.reactive-multi-axis-budget) |
| **Resource Scheduling** | ✅ Built-in | Priority queuing + preemption limits (agent-utilities OS-5.2) |

## Concept Registry

This project implements or inherits the following ecosystem concepts:

| Concept ID | Description | Source |
|:-----------|:------------|:-------|
| CY-OS.governance.data-export-live-insights | Data Export / Live Insights | `clarity-api` (this project) |
| ECO-4.1 | MCP & Universal Skills | `agent-utilities` (inherited) |
| AU-ECO.toolkit.journey-map-narrative | A2A Network & Consensus | `agent-utilities` (inherited) |

> 📖 **Full Registry**: See [`agent-utilities/docs/overview.md`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/overview.md) for the complete 5-Pillar concept index.

## Architecture

This project follows the standardized agent-package pattern:

```
clarity-api/
├── clarity_api/                 # Source code
│   ├── __init__.py
│   ├── agent_server.py          # A2A agent entry point (clarity-agent)
│   ├── api/                     # Modular REST client mixins
│   │   ├── api_client_base.py   # HTTP/REST base (session, auth, ssl, errors)
│   │   └── api_client_insights.py  # Data Export / insights domain client
│   ├── api_client.py            # Api facade composed from api/ mixins
│   ├── auth.py                  # get_client() dependency for MCP tools
│   ├── mcp/                     # Modular MCP tool registration
│   │   └── mcp_insights.py      # clarity_insights action-routed tool
│   └── mcp_server.py            # FastMCP server entry point (clarity-mcp)
├── tests/                       # Test suite
├── docs/                        # Documentation
├── pyproject.toml               # Package metadata
├── mcp_config.json              # MCP server configuration
└── docker/                      # Container deployment
```

## MCP Configuration

### stdio Mode
```json
{
  "mcpServers": {
    "clarity-api": {
      "command": "uv",
      "args": ["run", "--with", "clarity-api", "clarity-mcp"],
      "env": {}
    }
  }
}
```

### Streamable HTTP Mode
```bash
clarity-mcp --transport streamable-http --port 8001
```
