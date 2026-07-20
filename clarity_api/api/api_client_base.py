#!/usr/bin/python
"""HTTP/REST base client for the Microsoft Clarity Data Export API.

Provides the shared ``requests.Session``, bearer-token authentication header,
named TLS-profile handling, base-URL normalization, and credential validation that all
domain client mixins build on. Validation hits ``GET /projects`` during
``__init__`` to fail fast on bad credentials — preserving the original
``clarity_api.clarity_api.Api`` contract.
"""

import logging

import requests
from agent_utilities.core.transport_security import (
    ResolvedTLSProfile,
    resolve_configured_tls_profile,
)

from clarity_api.exceptions import (
    AuthError,
    MissingParameterError,
    ParameterError,
    UnauthorizedError,
)

logger = logging.getLogger(__name__)


class ClarityApiBase:
    """Base HTTP client for Microsoft Clarity.

    CONCEPT:CY-OS.governance.rest-base-client-owns — REST Base Client. Owns the shared ``requests.Session``,
    bearer-token header, named TLS-profile handling, and fail-fast credential
    validation against ``GET /projects``.

    Args:
        url: Base URL of the Clarity instance (e.g. ``https://www.clarity.ms``).
        token: Bearer API token generated from the Clarity project settings.
        tls_profile: Resolved mandatory-verification transport policy.
        debug: Enable verbose logging when ``True``.

    Raises:
        MissingParameterError: If ``url`` or ``token`` is not provided.
        UnauthorizedError: If the token is rejected (HTTP 403).
        AuthError: If authentication fails (HTTP 401).
        ParameterError: If the validation endpoint is not found (HTTP 404).
    """

    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        tls_profile: ResolvedTLSProfile | None = None,
        debug: bool = False,
    ):
        """Initialize the session and validate credentials (CONCEPT:CY-OS.governance.rest-base-client-owns)."""
        if debug:
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
        else:
            logger.setLevel(logging.ERROR)

        if url is None:
            raise MissingParameterError

        self.tls_profile = tls_profile or resolve_configured_tls_profile("clarity")
        self._session = self.tls_profile.configure_requests_session(requests.Session())
        self.url = url.rstrip("/")
        self.headers: dict | None = None
        self.debug = debug

        if token:
            self.headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        else:
            raise MissingParameterError

        response = self._session.get(
            url=f"{self.url}/projects",
            headers=self.headers,
            timeout=10,
        )

        if response.status_code == 403:
            logger.error("Clarity authorization rejected the request")
            raise UnauthorizedError
        elif response.status_code == 401:
            logger.error("Clarity authentication rejected the request")
            raise AuthError
        elif response.status_code == 404:
            logger.error("Clarity resource lookup failed")
            raise ParameterError

    def close(self) -> None:
        """Release transport resources and runtime-only TLS material."""
        self._session.close()
        self.tls_profile.cleanup()

    def api_request(
        self,
        method: str = "GET",
        endpoint: str = "/",
        params: dict | None = None,
        json: dict | None = None,
    ) -> requests.Response:
        """Execute an arbitrary REST request against the Clarity instance.

        CONCEPT:CY-OS.governance.rest-base-client-owns — REST Base Client.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH).
            endpoint: Path appended to the base URL (e.g. ``/projects``).
            params: Optional query parameters.
            json: Optional JSON body payload.

        Returns:
            The raw ``requests.Response`` object.
        """
        url = f"{self.url}/{endpoint.lstrip('/')}"
        return self._session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json,
            headers=self.headers,
        )
