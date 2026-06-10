"""Application-service layer for clarity-api.

Thin, dependency-injected use-case services that sit between the MCP transport
layer and the REST adapter (``clarity_api.api``).
"""

from clarity_api.services.insights_service import InsightsService

__all__ = ["InsightsService"]
