"""Clarity Authentication Module.

Authentication priority:
1. **OIDC Delegation** — If delegation is active, exchanges the IdP-issued
   user token for a downstream Clarity access token via RFC 8693 Token Exchange
   using the shared ``delegated_auth`` helper.
2. **Fixed Credentials** — Falls back to the ``CLARITY_TOKEN`` env var.

Environment variables:
- ``CLARITY_URL`` — base URL of the Clarity instance (default ``https://www.clarity.ms``).
- ``CLARITY_TOKEN`` — bearer API token.
- ``CLARITY_SSL_VERIFY`` — whether to verify TLS certificates (default ``True``).
"""

import os
import threading

from agent_utilities.base_utilities import get_logger, to_boolean
from agent_utilities.core.exceptions import AuthError, UnauthorizedError

local = threading.local()
from clarity_api.api_client import Api

logger = get_logger(__name__)


def get_client(
    instance: str = os.getenv("CLARITY_URL", "https://www.clarity.ms"),
    token: str | None = os.getenv("CLARITY_TOKEN", None),
    verify: bool = to_boolean(string=os.getenv("CLARITY_SSL_VERIFY", "True")),
    config: dict | None = None,
) -> Api:
    """Factory function to create the Clarity ``Api`` client.

    Supports OIDC delegation and fixed credentials (token). Used as the
    ``Depends(get_client)`` dependency for the MCP tools.
    """
    from agent_utilities.mcp.delegated_auth import (
        get_delegated_token,
        get_user_identity,
        is_delegation_enabled,
    )

    delegation_enabled = is_delegation_enabled(config)

    # --- Path 1: OIDC Delegation (RFC 8693 Token Exchange) ---
    if delegation_enabled:
        try:
            delegated_token = get_delegated_token(
                config=config,
                audience=(config or {}).get("audience", instance),
                scopes=(config or {}).get("delegated_scopes", "api"),
                verify=verify,
            )
            identity = get_user_identity()
            logger.info(
                "Using OIDC delegated token for Clarity API",
                extra={
                    "user_email": identity.get("email"),
                    "instance": instance,
                },
            )
            return Api(url=instance, token=delegated_token, verify=verify)
        except Exception as e:
            logger.error(
                "OIDC delegation failed for Clarity",
                extra={"error_type": type(e).__name__, "error_message": str(e)},
            )
            raise RuntimeError(f"Token exchange failed: {str(e)}") from e

    # --- Path 2: Fixed Credentials (CLARITY_TOKEN) ---
    logger.info("Using fixed credentials for Clarity API")
    try:
        return Api(url=instance, token=token, verify=verify)
    except (AuthError, UnauthorizedError) as e:
        raise RuntimeError(
            f"AUTHENTICATION ERROR: The Clarity credentials provided are not valid for '{instance}'. "
            f"Please check your CLARITY_TOKEN and CLARITY_URL environment variables. "
            f"Error details: {str(e)}"
        ) from e
