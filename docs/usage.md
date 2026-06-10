# Usage

## Python `Api` client

```python
import clarity_api

client = clarity_api.Api(
    url="https://www.clarity.ms",
    token="<CLARITY_TOKEN>",
)

response = client.get_data_export(
    number_of_days=2,
    dimension_1="OS",
    dimension_2="Channel",
)
print(response.status_code)
print(response.json())
```

The original `from clarity_api.clarity_api import Api` import continues to work; it
re-exports the same facade.

### Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `number_of_days` / `numOfDays` | 1, 2, 3 | Last 24, 48, or 72 hours |
| `dimension_1` / `dimension1` | see below | First breakdown dimension |
| `dimension_2` / `dimension2` | see below | Second breakdown dimension |
| `dimension_3` / `dimension3` | see below | Third breakdown dimension |

**Dimension options**: `Browser`, `Device`, `Country`, `OS`, `Source`, `Medium`,
`Campaign`, `Channel`, `URL`.

## MCP server (`clarity-mcp`)

```bash
clarity-mcp                                       # stdio (default)
clarity-mcp --transport streamable-http --port 8000
clarity-mcp --transport sse --port 8000
```

### Available MCP tools

| Tool | Concept | Actions | Description |
|------|---------|---------|-------------|
| `clarity_insights` | `CONCEPT:CLA-001` | `get_data_export` | Export Clarity dashboard data / live insights |

Tools take an `action` plus a JSON `params_json` payload:

```json
{
  "action": "get_data_export",
  "params_json": "{\"number_of_days\": 3, \"dimension_1\": \"OS\"}"
}
```

### Dynamic tool selection

Each tool domain is gated behind an env toggle so deployments can trim their
surface:

| Toggle | Default | Domain |
|--------|---------|--------|
| `INSIGHTSTOOL` | `True` | `clarity_insights` |

## Agent server (`clarity-agent`)

```bash
clarity-agent --web --provider openai --model-id gpt-4o
```

The agent auto-discovers the MCP tools via `mcp_config.json` and exposes an
AG-UI web interface.
