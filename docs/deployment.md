# Deployment

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
