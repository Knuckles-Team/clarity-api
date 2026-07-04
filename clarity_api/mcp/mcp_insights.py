"""MCP tools for Microsoft Clarity data export / insights operations.

Implements ``CONCEPT:CY-OS.governance.data-export-live-insights`` (Data Export / Live Insights) using the
action-routed dynamic tool pattern: a single tool dispatches on ``action`` with
a JSON ``params_json`` payload.
"""

import json
from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from clarity_api.auth import get_client
from clarity_api.services import InsightsService


def _serialize(response: Any) -> Any:
    """Convert a ``requests.Response`` into an MCP-serializable structure."""
    if hasattr(response, "status_code"):
        try:
            body = response.json()
        except Exception:
            body = response.text if hasattr(response, "text") else None
        return {"status_code": response.status_code, "data": body}
    return response


def register_insights_tools(mcp: FastMCP):
    @mcp.tool(tags={"data-export"})
    async def clarity_insights(
        action: str = Field(
            default="get_data_export",
            description="Action to perform. Must be one of: 'get_data_export'",
        ),
        params_json: str = Field(
            default="{}",
            description=(
                "JSON string of parameters. Supports 'number_of_days' (1, 2, or 3), "
                "'dimension_1', 'dimension_2', 'dimension_3'. Dimension options: "
                "Browser, Device, Country, OS, Source, Medium, Campaign, Channel, URL."
            ),
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Retrieve Microsoft Clarity dashboard data insights for a project.

        CONCEPT:CY-OS.governance.data-export-live-insights — Data Export / Live Insights. Pulls live insights over
        a date range, optionally broken down by up to three dimensions.
        """
        if ctx:
            await ctx.info("Executing Clarity data export...")

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        service = InsightsService(client=client, serializer=_serialize)

        if action == "get_data_export":
            return service.get_data_export(**kwargs)
        raise ValueError(f"Unknown action: {action}")

    @mcp.tool(tags={"data-export"})
    async def clarity_ingest_insights(
        params_json: str = Field(
            default="{}",
            description=(
                "JSON string of export params. Supports 'number_of_days' (1, 2, or 3), "
                "'dimension_1', 'dimension_2', 'dimension_3'. Dimension options: "
                "Browser, Device, Country, OS, Source, Medium, Campaign, Channel, URL."
            ),
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Natively ingest a Clarity data export into the epistemic-graph knowledge graph.

        CONCEPT:CY-OS.governance.data-export-live-insights. Pulls the live-insights export
        via the client and pushes it as typed nodes — a ``:ClarityProject``, a
        ``:ClaritySession`` snapshot, one ``:BehaviorInsight`` per metric, and
        ``:BehaviorDimension`` breakdown nodes — plus a ``:Document`` summary, with
        their ``:belongsToProject`` / ``:hasInsight`` / ``:brokenDownBy`` links. Best
        effort: returns ``{"ingested": None}`` when no engine is reachable.
        """
        if ctx:
            await ctx.info("Ingesting Clarity export into the knowledge graph...")

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        from clarity_api.kg_ingest import ingest_response

        response = client.get_data_export(
            **{k: v for k, v in kwargs.items() if v is not None}
        )
        result = ingest_response(response, kwargs)
        return {"ingested": result}
