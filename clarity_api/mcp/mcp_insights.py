"""MCP tools for Microsoft Clarity data export / insights operations.

Implements ``CONCEPT:CY-OS.governance.data-export-live-insights`` (Data Export / Live Insights).
The read tool ``clarity_get_data_export`` is derived by the SDK from the client method;
this module registers the explicit graph-ingest tool.
"""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from clarity_api.auth import get_client


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
    async def clarity_ingest_insights(
        number_of_days: int | None = Field(
            default=None, description="Trailing window in days: 1, 2 or 3."
        ),
        dimension_1: str | None = Field(
            default=None,
            description="First breakdown: Browser, Device, Country, OS, Source, Medium, Campaign, Channel or URL.",
        ),
        dimension_2: str | None = Field(
            default=None, description="Second breakdown, same values."
        ),
        dimension_3: str | None = Field(
            default=None, description="Third breakdown, same values."
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

        kwargs = {
            k: v
            for k, v in {
                "number_of_days": number_of_days,
                "dimension_1": dimension_1,
                "dimension_2": dimension_2,
                "dimension_3": dimension_3,
            }.items()
            if v is not None
        }

        from clarity_api.kg_ingest import ingest_response

        response = client.get_data_export(**kwargs)
        result = await ingest_response(response, kwargs)
        return {"ingested": result}
