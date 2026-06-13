# Microsoft Clarity API

![PyPI - Version](https://img.shields.io/pypi/v/clarity-api)
![PyPI - Downloads](https://img.shields.io/pypi/dd/clarity-api)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/clarity-api)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/clarity-api)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/clarity-api)
![PyPI - License](https://img.shields.io/pypi/l/clarity-api)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/clarity-api)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/clarity-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/clarity-api)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/clarity-api)

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/clarity-api)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/clarity-api)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/clarity-api)

*Version: 1.2.0*

**Microsoft Clarity API + MCP Server + A2A Agent**

`clarity-api` is a typed, action-routed connector for the
[Microsoft Clarity Data Export API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api),
built on [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities). It
ships a Python `Api` client, a [FastMCP](https://github.com/jlowin/fastmcp) MCP server
(`clarity-mcp`), and an optional Pydantic-AI A2A agent server (`clarity-agent`).

It works with the dashboard data — structured over a specified date range and broken
down by up to three dimensions.

This repository is actively maintained — contributions are welcome!

## Table of Contents

- [Architecture](#architecture)
- [Key Features](#key-features)
- [Available MCP Tools](#available-mcp-tools)
- [Dynamic Tool Selection](#dynamic-tool-selection)
- [Environment Variables](#environment-variables)
- [Configuration](#configuration)
- [Agent](#agent)
- [Usage (Python client)](#usage-python-client)
- [Security & Governance](#security--governance)
- [Installation](#installation)
- [Documentation](#documentation)
- [Contributing](#contributing)

## Architecture

`clarity-api` follows the standard agent-package layering: a typed REST client at
the bottom, an action-routed MCP tool layer in the middle, and an optional
Pydantic-AI A2A agent server on top. The MCP tool depends on an injected client
via `Depends(get_client)`, which resolves credentials (OIDC delegation or a fixed
`CLARITY_TOKEN`) before talking to the Microsoft Clarity REST API.

```mermaid
graph TD
    User(["User / A2A Client"]) --> Agent["clarity-agent<br/>Pydantic-AI A2A Server"]
    Agent --> MCP["clarity-mcp<br/>FastMCP Server"]
    MCP --> Tool["clarity_insights tool<br/>(CONCEPT:CLA-001)"]
    Tool -->|Depends get_client| Auth["get_client<br/>auth.py"]
    Tool --> Service["InsightsService<br/>clarity_api/services/"]
    Auth --> Client["Api facade<br/>clarity_api/api/"]
    Service --> Client
    Client --> Clarity(["Microsoft Clarity<br/>Data Export REST API"])
```

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Agent | `clarity_api/agent_server.py` | Pydantic-AI A2A server, AG-UI web interface |
| Tooling | `clarity_api/mcp/`, `clarity_api/mcp_server.py` | Action-routed MCP tool registration |
| Service | `clarity_api/services/` | `InsightsService` — dependency-injected data-export use case |
| Auth seam | `clarity_api/auth.py` | `get_client` dependency: OIDC delegation / fixed token |
| Client | `clarity_api/api/` | `ClarityApiBase` + `ClarityApiInsights` mixins composed into `Api` |
| Models | `clarity_api/clarity_models.py` | Pydantic request/response validation |

## Key Features

- **Typed Python client** — `clarity_api.api_client.Api`, composed from modular per-domain
  mixins in `clarity_api/api/`, validating credentials against `GET /projects`.
- **Action-routed MCP tool** — `clarity_insights` (`CONCEPT:CLA-001`) consolidates the
  Data Export surface to minimize LLM token overhead.
- **A2A agent server** — `clarity-agent` auto-discovers the MCP tools and exposes an
  AG-UI web interface.
- **Enterprise-ready** — inherits OIDC auth, OpenTelemetry, audit logging, prompt-injection
  defense, and guardrails from `agent-utilities`.

## Available MCP Tools

| Tool | Concept | Actions | Description |
|------|---------|---------|-------------|
| `clarity_insights` | `CONCEPT:CLA-001` | `get_data_export` | Export Clarity dashboard data / live insights |

### Parameters
- `number_of_days` (1, 2, or 3): last 24, 48, or 72 hours.
- `dimension_1`, `dimension_2`, `dimension_3`: breakdown dimensions.

#### Dimension Options
`Browser`, `Device`, `Country`, `OS`, `Source`, `Medium`, `Campaign`, `Channel`, `URL`.

## Dynamic Tool Selection

Each tool domain is gated behind an env toggle so deployments can trim their surface:

| Toggle | Default | Domain |
|--------|---------|--------|
| `INSIGHTSTOOL` | `True` | `clarity_insights` |

## Environment Variables

All runtime configuration is supplied via environment variables (or a `.env`
file — see [`.env.example`](.env.example)). Never commit real tokens.

### Clarity credentials

| Variable | Default | Description |
|----------|---------|-------------|
| `CLARITY_URL` | `https://www.clarity.ms` | Base URL of the Microsoft Clarity instance. |
| `CLARITY_TOKEN` | _(none)_ | Bearer API token generated in the Clarity project settings. Required unless OIDC delegation is enabled. |
| `CLARITY_SSL_VERIFY` | `True` | Whether to verify TLS certificates when calling the Clarity API. |

### MCP server / transport

| Variable | Default | Description |
|----------|---------|-------------|
| `TRANSPORT` | `stdio` | MCP transport: `stdio`, `streamable-http`, or `sse`. |
| `HOST` | `0.0.0.0` | Bind host for HTTP transports. |
| `PORT` | `8000` | Bind port for HTTP transports. |
| `AUTH_TYPE` | `none` | MCP server auth scheme inherited from `agent-utilities` (e.g. `none`, `oidc`). |
| `FASTMCP_LOG_LEVEL` | `ERROR` | FastMCP log verbosity. Set to `ERROR` at startup to suppress log spam. |
| `INSIGHTSTOOL` | `True` | Toggle registration of the `clarity_insights` tool (see [Dynamic Tool Selection](#dynamic-tool-selection)). |

### Telemetry & access governance

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_OTEL` | `True` | Enable OpenTelemetry export of traces/metrics. |
| `EUNOMIA_TYPE` | `none` | Eunomia authorization mode: `none`, `embedded`, or `remote`. |
| `EUNOMIA_POLICY_FILE` | `mcp_policies.json` | Path to the local Eunomia policy file (embedded mode). |

### Build / terminal (set automatically — usually no action needed)

| Variable | Default | Description |
|----------|---------|-------------|
| `UV_COMPILE_BYTECODE` | `1` | Set in the Docker image to precompile bytecode for faster cold starts. |
| `NO_COLOR` / `TERM` | `1` / `dumb` | Terminal-control variables set at MCP startup to keep stdio transport output machine-clean. Not app configuration — listed for completeness. |

## Configuration

### stdio (local agent integration)

```json
{
  "mcpServers": {
    "clarity-api": {
      "command": "uv",
      "args": ["run", "--with", "clarity-api", "clarity-mcp"],
      "env": {
        "CLARITY_URL": "https://www.clarity.ms",
        "CLARITY_TOKEN": "<YOUR_CLARITY_TOKEN>"
      }
    }
  }
}
```

### Streamable HTTP

```bash
export CLARITY_URL=https://www.clarity.ms
export CLARITY_TOKEN=<your-clarity-token>
clarity-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker pull knucklessg1/clarity-api:latest
docker compose -f docker/mcp.compose.yml up -d
```

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`clarity-api` can also run as a **local container** (Docker / Podman / `uv`) or be
consumed from a **remote deployment**. The
[Deployment guide](https://knuckles-team.github.io/clarity-api/deployment/) has full, copy-paste
`mcp_config.json` for all four transports — **stdio**, **streamable-http**,
**local container / uv**, and **remote URL**:

- **Local container / uv** — launch the server from `mcp_config.json` via `uvx`,
  `docker run`, or `podman run`, or point at a local streamable-http container by `url`.
- **Remote URL** — connect to a server deployed behind Caddy at
  `http://clarity-mcp.arpa/mcp` using the `"url"` key.
<!-- END GENERATED: additional-deployment-options -->

## Agent

The `clarity-agent` entry point (`clarity_api/agent_server.py`) starts a
Pydantic-AI A2A server that auto-discovers the MCP tools and exposes an AG-UI web
interface.

### Run locally

```bash
clarity-agent --web --provider openai --model-id gpt-4o
```

The agent reads its identity from `clarity_api/agent_data/IDENTITY.md` and discovers
tools via `mcp_config.json`.

### Deploy with Docker Compose

`docker/agent.compose.yml` runs the MCP server and the agent server side by side;
the agent connects to the MCP server over `MCP_URL`:

```yaml
services:
  clarity-api-mcp:
    image: knucklessg1/clarity-api:latest
    restart: always
    env_file: [ ../.env ]
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
    ports: [ "8000:8000" ]

  clarity-api-agent:
    image: knucklessg1/clarity-api:latest
    restart: always
    depends_on: [ clarity-api-mcp ]
    command: [ "clarity-agent" ]
    env_file: [ ../.env ]
    environment:
      - HOST=0.0.0.0
      - PORT=9017
      - MCP_URL=http://clarity-api-mcp:8000/mcp
      - PROVIDER=${PROVIDER:-openai}
      - MODEL_ID=${MODEL_ID:-gpt-4o}
      - ENABLE_WEB_UI=True
      - ENABLE_OTEL=True
    ports: [ "9017:9017" ]
```

```bash
docker compose -f docker/agent.compose.yml up -d
```

## Usage (Python client)

```python
#!/usr/bin/python
# coding: utf-8
import clarity_api

token = "<TOKEN>"
url = "https://www.clarity.ms"
client = clarity_api.Api(url=url, token=token)

response = client.get_data_export(number_of_days=2, dimension_1="OS", dimension_2="Channel")
print("Status Code:", response.status_code)
print("JSON Output:", response.json())
```

## Security & Governance

`clarity-api` inherits enterprise infrastructure from `agent-utilities`: JWT/OIDC
authentication, OpenTelemetry instrumentation, HashiCorp Vault secret resolution,
append-only audit logging (agent-utilities `OS-5.4`), prompt-injection defense
(`OS-5.1`), and the guardrail engine (`OS-5.3`). The connector stays
inactive until `CLARITY_URL` and `CLARITY_TOKEN` are configured. Never commit `.env`
files or tokens.

## Installation

```bash
python -m pip install "clarity-api[all]"
```

| Extra | Use for |
|-------|---------|
| _(none)_ | the `Api` client |
| `mcp` | the `clarity-mcp` MCP server |
| `agent` | the `clarity-agent` A2A agent |
| `all` | everything |

### Obtaining Access Tokens
**Note**: Only project admins can manage access tokens.

1. Go to your Clarity project. Select `Settings` → `Data Export` → `Generate new API token`.
2. Provide a descriptive name for the token for easy identification.

## Documentation

- [Documentation site](https://knuckles-team.github.io/clarity-api/)
- [Overview](docs/overview.md)
- [Installation](docs/installation.md)
- [Usage](docs/usage.md)
- [Deployment](docs/deployment.md)
- [Concepts](docs/concepts.md)

## Contributing

Contributions are welcome. Run quality checks before pushing:

```bash
pre-commit run --all-files
python -m pytest -q
```
