# Deployment

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`clarity-api` supports local stdio, a loopback-only development listener, a
least-privilege stdio container, and a remote authenticated HTTPS boundary.
Provider endpoint, credential, selector, identity, and trust material are supplied
at runtime through `AgentConfig`; none is stored in this repository.

### Installed stdio process

```json
{
  "mcpServers": {
    "clarity": {
      "command": "clarity-mcp",
      "args": [],
      "env": {"MCP_TOOL_MODE": "intent"}
    }
  }
}
```

### Loopback development listener

```bash
clarity-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Do not expose this listener beyond loopback. Network deployments require direct TLS
or an explicitly trusted TLS-terminating ingress, configured authentication, exact
`MCP_ALLOWED_HOSTS`, and an exact trusted-proxy CIDR policy.

### Least-privilege local container

```bash
docker run -i --rm \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  --pids-limit=256 \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m \
  -e TRANSPORT=stdio \
  registry.example.invalid/clarity-api@sha256:<digest> clarity-mcp
```

The operator projects the selected AgentConfig profile into the process at runtime;
the image remains immutable and contains no environment connection profile.

### Remote authenticated HTTPS endpoint

```json
{
  "mcpServers": {
    "clarity": {"url": "https://service.example.invalid/mcp"}
  }
}
```

Store the real remote URL, outbound identity reference, and TLS-profile reference in
`AgentConfig`, not in MCP client JSON or documentation.
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
docker build -f docker/Dockerfile -t example/clarity-api:agent-local .
```

A `docker/debug.Dockerfile` is provided for an in-place editable install with
shell tooling and the Starship prompt.

## Environment

| Variable | Description |
|----------|-------------|
| `CLARITY_URL` | Base URL of the Clarity instance |
| `CLARITY_TOKEN` | Bearer API token |
| `TLS_PROFILE` / `TLS_PROFILE_REF` | AgentConfig private-CA/mTLS profile; verification remains mandatory |
| `HOST` / `PORT` / `TRANSPORT` | MCP server bind + transport |
| `INSIGHTSTOOL` | Toggle the insights tool domain |

## Transports

- **stdio** — default, for local agent integration.
- **streamable-http** — for networked deployments behind a reverse proxy.
- **sse** — server-sent events transport.
