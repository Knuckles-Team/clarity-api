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
        self, api_parameters: dict | None = None, **kwargs
    ) -> requests.Response:
        """Retrieve dashboard data insights for a project.

        CONCEPT:CLA-001 — Data Export / Live Insights. Implements the
        ``GET /export-data/api/v1/project-live-insights`` call backing the
        ``clarity_insights`` MCP tool.

        Accepts either a pre-built ``api_parameters`` dict or keyword arguments
        (``number_of_days``/``numOfDays``, ``dimension_1``/``dimension1``, etc.),
        which are validated and normalized via :class:`InputModel`.

        Args:
            api_parameters: Pre-built query parameter dict. When omitted, the
                parameters are constructed from ``kwargs`` via ``InputModel``.
            **kwargs: Convenience keyword arguments forwarded to ``InputModel``.

        Returns:
            The ``requests.Response`` object from the GET request.

        Raises:
            ParameterError: If the provided parameters fail validation.
        """
        try:
            if api_parameters is None:
                model = InputModel(**kwargs)
                api_parameters = model.api_parameters

            response = self._session.get(
                url=f"{self.url}/export-data/api/v1/project-live-insights",
                params=api_parameters,
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response
