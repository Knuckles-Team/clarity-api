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

*Version: 1.0.0*

**Microsoft Clarity API + MCP Server + A2A Agent**

`clarity-api` is a typed, action-routed connector for the
[Microsoft Clarity Data Export API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api),
built on [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities). It
ships a Python `Api` client, a [FastMCP](https://github.com/jlowin/fastmcp) MCP server
(`clarity-mcp`), and an optional Pydantic-AI A2A agent server (`clarity-agent`).

It works with the dashboard data — structured over a specified date range and broken
down by up to three dimensions.

This repository is actively maintained — contributions are welcome!

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

## Agent

```bash
clarity-agent --web --provider openai --model-id gpt-4o
```

The agent reads its identity from `clarity_api/agent_data/IDENTITY.md` and discovers
tools via `mcp_config.json`.

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
append-only audit logging (`CONCEPT:OS-5.4`), prompt-injection defense
(`CONCEPT:OS-5.1`), and the guardrail engine (`CONCEPT:OS-5.3`). The connector stays
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
