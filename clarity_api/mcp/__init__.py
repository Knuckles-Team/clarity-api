"""MCP tool registration modules for clarity-api.

Each domain has its own module with a ``register_*_tools`` function.
"""

from clarity_api.mcp.mcp_insights import register_insights_tools

__all__ = [
    "register_insights_tools",
]
