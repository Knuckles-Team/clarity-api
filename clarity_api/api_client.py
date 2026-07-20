#!/usr/bin/python
"""Top-level Clarity API client facade.

Composes the per-domain client mixins from :mod:`clarity_api.api` into a single
``Api`` class. The constructor validates credentials
against ``GET /projects``, plus ``get_data_export``) while routing the actual
implementation through the modular ``api/`` sub-package.
"""

from clarity_api.api.api_client_insights import ClarityApiInsights


class Api(ClarityApiInsights):
    """Microsoft Clarity Data Export API client.

    Args:
        url: Base URL of the Clarity instance (e.g. ``https://www.clarity.ms``).
        token: Bearer API token from the Clarity project settings.
        tls_profile: Resolved mandatory-verification transport policy.
    """

    __slots__ = ()


__all__ = ["Api"]
