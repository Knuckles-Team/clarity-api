"""Application-service layer for Clarity data-export use cases.

Sits between the MCP tool (transport) and the ``Api`` client (adapter),
providing a thin, dependency-injected seam that keeps tool-registration code
free of business logic.

Implements ``CONCEPT:CY-OS.governance.data-export-live-insights`` (Data Export / Live Insights) at the
application-service boundary.
"""

from typing import Any, Protocol

import requests


class DataExportClient(Protocol):
    """Structural type for the only client capability this service needs.

    Captures the actual dependency contract — a client exposing
    ``get_data_export`` — so both the concrete
    :class:`~clarity_api.api_client.Api` and lightweight test doubles satisfy
    it without an inheritance coupling.
    """

    def get_data_export(self, **kwargs: Any) -> requests.Response: ...


class InsightsService:
    """Use-case service for Clarity insights, built around an injected client.

    Args:
        client: Any client exposing ``get_data_export`` — typically a
            configured :class:`~clarity_api.api_client.Api` instance resolved
            via ``Depends(get_client)``.
        serializer: Callable that converts a ``requests.Response`` into an
            MCP-serializable structure. Injected for testability.
    """

    def __init__(self, client: DataExportClient, serializer: Any) -> None:
        self._client = client
        self._serialize = serializer

    def get_data_export(self, **kwargs: Any) -> Any:
        """Execute a Clarity data export and return a serialized payload.

        CONCEPT:CY-OS.governance.data-export-live-insights — Data Export / Live Insights. Strips ``None`` values
        from ``kwargs`` and delegates to the injected client, then serializes.
        """
        clean = {k: v for k, v in kwargs.items() if v is not None}
        return self._serialize(self._client.get_data_export(**clean))


__all__ = ["InsightsService"]
