# Installation

`clarity-api` is published to PyPI and ships a prebuilt Docker image.

## From PyPI

```bash
# Core client only
pip install clarity-api

# With the MCP server (clarity-mcp)
pip install "clarity-api[mcp]"

# With the A2A agent server (clarity-agent)
pip install "clarity-api[agent]"

# Everything
pip install "clarity-api[all]"
```

## From source

```bash
git clone https://github.com/Knuckles-Team/clarity-api.git
cd clarity-api
pip install -e ".[all]"
```

## Docker

```bash
docker pull example/clarity-api@sha256:<digest>
docker run --rm -e CLARITY_URL -e CLARITY_TOKEN example/clarity-api@sha256:<digest>
```

## Extras matrix

| Extra | Installs | Use for |
|-------|----------|---------|
| _(none)_ | `agent-utilities`, `requests`, `pydantic`, `python-dotenv` | the `Api` client |
| `mcp` | `agent-utilities[mcp]` | the `clarity-mcp` MCP server |
| `agent` | `agent-utilities[agent-runtime,logfire]` | the `clarity-agent` A2A agent |
| `all` | `clarity-api[mcp,agent]` | everything |
| `test` | pytest tooling | running the test suite |

## Credentials

Configure these environment variables (or a `.env` file — see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `CLARITY_URL` | `https://www.clarity.ms` | Base URL of the Clarity instance |
| `CLARITY_TOKEN` | _(unset)_ | Bearer API token from project settings |
| `TLS_PROFILE` / `TLS_PROFILE_REF` | _(system trust)_ | AgentConfig transport profile; verification remains mandatory |

> **Note**: Only Clarity project admins can generate API tokens
> (`Settings` → `Data Export` → `Generate new API token`).
