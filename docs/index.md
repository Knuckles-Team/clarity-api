# clarity-api

Microsoft Clarity **API + MCP Server + A2A Agent** for the agent-utilities ecosystem —
a typed, action-routed connector for the Clarity Data Export API.

!!! info "Official documentation"
    This site is the canonical reference for `clarity-api`, maintained alongside every
    release.

[![PyPI](https://img.shields.io/pypi/v/clarity-api)](https://pypi.org/project/clarity-api/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/clarity-api)](https://github.com/Knuckles-Team/clarity-api/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/clarity-api)

## Overview

`clarity-api` wraps the [Microsoft Clarity Data Export API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api)
with typed, deterministic MCP tools and an optional Pydantic-AI agent server. It provides:

- **`Api`** — a Python client (`clarity_api.api_client.Api`) composed from per-domain
  mixins. It validates credentials against `GET /projects` and exposes
  `get_data_export` for live dashboard insights.
- **Action-routed MCP tool** — the consolidated, togglable `clarity_insights` tool
  (`CONCEPT:CLA-001`) that minimizes token overhead in LLM contexts.
- **An A2A agent server** — a Pydantic-AI graph agent (console script `clarity-agent`)
  that calls the MCP tool surface and exposes an AG-UI web interface.

The connector remains inactive when credentials are absent: configure `CLARITY_URL`
and `CLARITY_TOKEN` to connect it to your Clarity project.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP and agent servers, Docker Compose.
- :material-console: **[Usage](usage.md)** — the MCP tools, the `Api` client, and the CLI.
- :material-sitemap: **[Overview](overview.md)** — the action-routed tool surface and architecture.
- :material-tag-multiple: **[Concepts](concepts.md)** — the `CONCEPT:CLA-*` registry.

</div>

## Quick start

```bash
pip install "clarity-api[mcp]"
clarity-mcp                        # stdio MCP server (default transport)
```

Connect it to a Clarity project:

```bash
export CLARITY_URL=https://www.clarity.ms
export CLARITY_TOKEN=<your-clarity-token>
clarity-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

See **[Installation](installation.md)** and **[Deployment](deployment.md)** for the
full matrix (PyPI extras, Docker image, all transports, the agent server).
