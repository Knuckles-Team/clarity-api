# CONN-CLARITY-API-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `clarity-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `clarity_api` from it.
