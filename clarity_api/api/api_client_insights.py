#!/usr/bin/python
"""Insights / Data Export domain client for the Microsoft Clarity API.

Wraps the ``GET /export-data/api/v1/project-live-insights`` endpoint, exposing
``get_data_export`` while preserving the original behavior of
``clarity_api.clarity_api.Api.get_data_export``.
"""

import requests
from pydantic import ValidationError

from clarity_api.api.api_client_base import ClarityApiBase
from clarity_api.clarity_models import InputModel
from clarity_api.decorators import require_auth
from clarity_api.exceptions import ParameterError


class ClarityApiInsights(ClarityApiBase):
    """Domain client for Clarity Data Export / Live Insights operations."""

    @require_auth
    def get_data_export(
        self,
        number_of_days: int | None = None,
        dimension_1: str | None = None,
        dimension_2: str | None = None,
        dimension_3: str | None = None,
        api_parameters: dict | None = None,
    ) -> requests.Response:
        """Retrieve dashboard data insights for a project.

        CONCEPT:CY-OS.governance.data-export-live-insights — Data Export / Live Insights. Implements the
        ``GET /export-data/api/v1/project-live-insights`` call backing the
        ``clarity_get_data_export`` MCP tool.

        Accepts either a pre-built ``api_parameters`` dict or the typed
        ``number_of_days`` and ``dimension_1`` to ``dimension_3`` arguments, which are
        validated and normalized via :class:`InputModel`.

        Args:
            number_of_days: Trailing window in days; the API accepts 1, 2 or 3.
            dimension_1: First breakdown (Browser, Device, Country, OS, Source,
                Medium, Campaign, Channel or URL).
            dimension_2: Second breakdown, same values.
            dimension_3: Third breakdown, same values.
            api_parameters: Pre-built query parameter dict. When omitted, the
                parameters are constructed from the typed arguments via ``InputModel``.

        Returns:
            The ``requests.Response`` object from the GET request.

        Raises:
            ParameterError: If the provided parameters fail validation.
        """
        try:
            if api_parameters is None:
                given = {
                    "number_of_days": number_of_days,
                    "dimension_1": dimension_1,
                    "dimension_2": dimension_2,
                    "dimension_3": dimension_3,
                }
                model = InputModel(**{k: v for k, v in given.items() if v is not None})
                api_parameters = model.api_parameters

            response = self._session.get(
                url=f"{self.url}/export-data/api/v1/project-live-insights",
                params=api_parameters,
                headers=self.headers,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response
