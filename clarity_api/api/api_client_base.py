#!/usr/bin/python
# coding: utf-8
"""HTTP/REST base client for the Microsoft Clarity Data Export API.

Provides the shared ``requests.Session``, bearer-token authentication header,
SSL-verify handling, base-URL normalization, and credential validation that all
domain client mixins build on. Validation hits ``GET /projects`` during
``__init__`` to fail fast on bad credentials — preserving the original
``clarity_api.clarity_api.Api`` contract.
"""

import logging

import requests
import urllib3

from clarity_api.exceptions import (
    AuthError,
    MissingParameterError,
    ParameterError,
    UnauthorizedError,
)

logger = logging.getLogger(__name__)


class ClarityApiBase:
    """Base HTTP client for Microsoft Clarity.

    Args:
        url: Base URL of the Clarity instance (e.g. ``https://www.clarity.ms``).
        token: Bearer API token generated from the Clarity project settings.
        verify: Whether to verify TLS certificates. Defaults to ``True``.
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
        verify: bool = True,
        debug: bool = False,
    ):
        if debug:
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
        else:
            logger.setLevel(logging.ERROR)

        if url is None:
            raise MissingParameterError

        self._session = requests.Session()
        self.url = url.rstrip("/")
        self.headers: dict | None = None
        self.verify = verify
        self.debug = debug

        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
            verify=self.verify,
            timeout=10,
        )

        if response.status_code == 403:
            logger.error(f"Unauthorized Error: {response.content!r}")
            raise UnauthorizedError
        elif response.status_code == 401:
            logger.error(f"Authentication Error: {response.content!r}")
            raise AuthError
        elif response.status_code == 404:
            logger.error(f"Parameter Error: {response.content!r}")
            raise ParameterError

    def api_request(
        self,
        method: str = "GET",
        endpoint: str = "/",
        params: dict | None = None,
        json: dict | None = None,
    ) -> requests.Response:
        """Execute an arbitrary REST request against the Clarity instance.

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
            verify=self.verify,
        )
