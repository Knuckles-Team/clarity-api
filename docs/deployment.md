# Deployment

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`clarity-api` exposes its MCP server (console script `clarity-mcp`) four ways. Pick the row that
matches where the server runs relative to your MCP client, then copy the matching
`mcp_config.json` below. Replace the `<your-…>` placeholders with the values from the **Configuration / Environment Variables** section.

| # | Option | Transport | Where it runs | `mcp_config.json` key |
|---|--------|-----------|---------------|------------------------|
| 1 | stdio | `stdio` | client launches a subprocess | `command` |
| 2 | Streamable-HTTP (local) | `streamable-http` | a local network port | `command` or `url` |
| 3 | Local container / uv | `stdio` or `streamable-http` | Docker / Podman / uv on this host | `command` or `url` |
| 4 | Remote URL | `streamable-http` | a remote host behind Caddy | `url` |

### 1. stdio (local subprocess)

The client launches the server over stdio via `uvx` — best for local IDEs
(Cursor, Claude Desktop, VS Code):

```json
{
  "mcpServers": {
    "clarity-mcp": {
      "command": "uvx",
      "args": ["--from", "clarity-api", "clarity-mcp"],
      "env": {
        "CLARITY_URL": "<your-clarity_url>",
        "CLARITY_TOKEN": "<your-clarity_token>"
      }
    }
  }
}
```

### 2. Streamable-HTTP (local process)

Run the server as a long-lived HTTP process:

```bash
uvx --from clarity-api clarity-mcp --transport streamable-http --host 0.0.0.0 --port 8000
curl -s http://localhost:8000/health        # {"status":"OK"}
```

Then either let the client launch it:

```json
{
  "mcpServers": {
    "clarity-mcp": {
      "command": "uvx",
      "args": ["--from", "clarity-api", "clarity-mcp", "--transport", "streamable-http", "--port", "8000"],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "CLARITY_URL": "<your-clarity_url>",
        "CLARITY_TOKEN": "<your-clarity_token>"
      }
    }
  }
}
```

…or connect to the already-running process by URL:

```json
{
  "mcpServers": {
    "clarity-mcp": { "url": "http://localhost:8000/mcp" }
  }
}
```

### 3. Local container / uv

**(a) Launch a container directly from `mcp_config.json`** (stdio over the container —
no ports to manage). Swap `docker` for `podman` for a daemonless runtime:

```json
{
  "mcpServers": {
    "clarity-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "TRANSPORT=stdio",
        "-e", "CLARITY_URL=<your-clarity_url>",
        "-e", "CLARITY_TOKEN=<your-clarity_token>",
        "knucklessg1/clarity-api:latest"
      ]
    }
  }
}
```

**(b) Run a local streamable-http container, then connect by URL:**

```bash
docker run -d --name clarity-mcp -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e PORT=8000 \
  -e CLARITY_URL="<your-clarity_url>" \
  -e CLARITY_TOKEN="<your-clarity_token>" \
  knucklessg1/clarity-api:latest
# or, from a clone of this repo:
docker compose -f docker/mcp.compose.yml up -d
```

```json
{
  "mcpServers": {
    "clarity-mcp": { "url": "http://localhost:8000/mcp" }
  }
}
```

**(c) From a local checkout with `uv`:**

```bash
uv run clarity-mcp --transport streamable-http --port 8000
```

### 4. Remote URL (deployed behind Caddy)

When the server is deployed remotely (e.g. as a Docker service) and published through
Caddy on the internal `*.arpa` zone, connect with the `"url"` key — no local process or
image required:

```json
{
  "mcpServers": {
    "clarity-mcp": { "url": "http://clarity-mcp.arpa/mcp" }
  }
}
```

Caddy reverse-proxies `http://clarity-mcp.arpa` to the container's `:8000`
streamable-http listener; `http://clarity-mcp.arpa/health` returns
`{"status":"OK"}` when the service is live.
<!-- END GENERATED: deployment-options -->

## Docker Compose (MCP only)

```bash
cp .env.example .env   # fill in CLARITY_URL / CLARITY_TOKEN
docker compose -f docker/mcp.compose.yml up -d
```

The MCP server listens on port `8000` (streamable-http) with a `/health` check.

## Docker Compose (MCP + Agent)

```bash
docker compose -f docker/agent.compose.yml up -d
```

This brings up both the `clarity-api-mcp` service (port 8000) and the
`clarity-api-agent` service (port 9017, AG-UI web interface).

## Building the image

```bash
docker build -f docker/Dockerfile -t knucklessg1/clarity-api:latest .
```

A `docker/debug.Dockerfile` is provided for an in-place editable install with
shell tooling and the Starship prompt.

## Environment

| Variable | Description |
|----------|-------------|
| `CLARITY_URL` | Base URL of the Clarity instance |
| `CLARITY_TOKEN` | Bearer API token |
| `CLARITY_SSL_VERIFY` | Verify TLS certificates (`True`/`False`) |
| `HOST` / `PORT` / `TRANSPORT` | MCP server bind + transport |
| `INSIGHTSTOOL` | Toggle the insights tool domain |

## Transports

- **stdio** — default, for local agent integration.
- **streamable-http** — for networked deployments behind a reverse proxy.
- **sse** — server-sent events transport.
