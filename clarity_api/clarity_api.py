#!/usr/bin/python
"""Backward-compatibility shim for ``clarity_api.clarity_api.Api``.

The real implementation now lives in the modular :mod:`clarity_api.api`
sub-package and is composed by :mod:`clarity_api.api_client`. This module
re-exports ``Api`` so that existing imports
(``from clarity_api.clarity_api import Api``) keep working unchanged.
"""

from clarity_api.api_client import Api

__all__ = ["Api"]
