"""Tests that MCP tools register correctly on a FastMCP instance."""

import pytest


async def _list_tool_names(mcp) -> set:
    """Return registered tool names across FastMCP API versions."""
    if hasattr(mcp, "get_tools"):
        return set((await mcp.get_tools()).keys())
    if hasattr(mcp, "list_tools"):
        return {t.name for t in await mcp.list_tools()}
    raise AssertionError("No known tool-listing API on FastMCP instance")


@pytest.mark.asyncio
@pytest.mark.concept("CLA-001")
async def test_concept_cla_001_insights_tool_registers():
    """CLA-001: the data-export tool registers on a bare FastMCP instance."""
    from fastmcp import FastMCP

    from clarity_api.mcp import register_insights_tools

    mcp = FastMCP(name="test-clarity")
    register_insights_tools(mcp)

    names = await _list_tool_names(mcp)
    assert "clarity_insights" in names


@pytest.mark.asyncio
@pytest.mark.concept("CLA-001")
async def test_concept_cla_001_get_mcp_instance_builds():
    """CLA-001: the assembled MCP server exposes the data-export tool."""
    from agent_connector_sdk.connector import build_server

    _, mcp = build_server("clarity_api", command_args=[])
    names = await _list_tool_names(mcp)
    assert "clarity_get_data_export" in names
