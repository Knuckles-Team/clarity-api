"""Clarity Authentication Module.

Authentication priority:
1. **OIDC Delegation** — If delegation is active, exchanges the IdP-issued
   user token for a downstream Clarity access token via RFC 8693 Token Exchange
   using the SDK's ``agent_connector_sdk.auth.delegation`` helpers.
2. **Fixed Credentials** — Falls back to the ``CLARITY_TOKEN`` env var.

Environment variables:
- ``CLARITY_URL`` — base URL of the Clarity instance (default ``https://www.clarity.ms``).
- ``CLARITY_TOKEN`` — bearer API token.
"""

import logging
import threading

import httpx
from agent_connector_sdk.auth.delegation import (
    DelegationSettings,
    current_user_identity,
    current_user_token,
    exchange_token,
)
from agent_connector_sdk.config import setting
from agent_connector_sdk.exceptions import AuthError, UnauthorizedError
from agent_connector_sdk.tls.profile import ResolvedTLSProfile
from agent_connector_sdk.tls.resolve import resolve_tls_profile

local = threading.local()
from clarity_api.api_client import Api

logger = logging.getLogger(__name__)


def get_client(
    instance: str | None = None,
    token: str | None = None,
    tls_profile: ResolvedTLSProfile | None = None,
    config: dict | None = None,
) -> Api:
    """Factory function to create the Clarity ``Api`` client.

    CONCEPT:CY-OS.identity.credential-auth-factory-supports — Credential & Auth Factory. Supports OIDC delegation
    (RFC 8693 token exchange) and fixed credentials (``CLARITY_TOKEN``). Used as
    the ``Depends(get_client)`` dependency for the MCP tools.
    """
    if instance is None:
        instance = setting("CLARITY_URL", "https://www.clarity.ms")
    if token is None:
        token = setting("CLARITY_TOKEN", None)
    profile = tls_profile or resolve_tls_profile("clarity")

    delegation = DelegationSettings.from_settings()

    # --- Path 1: OIDC Delegation (RFC 8693 Token Exchange) ---
    if delegation.enabled:
        try:
            subject_token = current_user_token()
            if not subject_token:
                raise AuthError("no verified caller token to delegate")
            with httpx.Client(timeout=30.0) as http_client:
                access_token = exchange_token(
                    delegation,
                    subject_token=subject_token,
                    http_client=http_client,
                )
            identity_ref = current_user_identity()
            logger.info(
                "Using OIDC delegated token for Clarity API",
                extra={
                    "identity_ref": identity_ref,
                    "instance": instance,
                },
            )
            return Api(url=instance, token=access_token.value, tls_profile=profile)
        except Exception as e:
            logger.error(
                "OIDC delegation failed for Clarity",
                extra={
                    "error_type": type(e).__name__,
                    "error_message": type(e).__name__,
                },
            )
            raise RuntimeError(f"Token exchange failed: {type(e).__name__}") from e

    # --- Path 2: Fixed Credentials (CLARITY_TOKEN) ---
    logger.info("Using fixed credentials for Clarity API")
    try:
        return Api(url=instance, token=token, tls_profile=profile)
    except (AuthError, UnauthorizedError) as e:
        raise RuntimeError(
            f"AUTHENTICATION ERROR: The Clarity credentials provided are not valid for '{instance}'. "
            f"Please check your CLARITY_TOKEN and CLARITY_URL environment variables. "
            f"Error details: {type(e).__name__}"
        ) from e
