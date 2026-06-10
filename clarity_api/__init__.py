#!/usr/bin/env python
"""Clarity API

A Python library, MCP server, and A2A agent for exporting data from
Microsoft Clarity.
"""

import importlib
import inspect
from typing import Any

from clarity_api.version import __author__, __credits__, __version__

__all__: list[str] = ["__version__", "__author__", "__credits__"]

CORE_MODULES: list[str] = [
    "clarity_api.clarity_models",
    "clarity_api.api_client",
]

OPTIONAL_MODULES = {
    "clarity_api.agent_server": "agent",
    "clarity_api.mcp_server": "mcp",
}


def _expose_members(module):
    """Expose public classes and functions from a module into globals and __all__."""
    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) or inspect.isfunction(obj)) and not name.startswith(
            "_"
        ):
            globals()[name] = obj
            if name not in __all__:
                __all__.append(name)


# Eagerly import core modules (keeps API wrappers fast & light)
for module_name in CORE_MODULES:
    if module_name:
        _module = importlib.import_module(module_name)
        _expose_members(_module)

# Dynamic/lazy loading of optional modules (agent_server, mcp_server)
_loaded_optional_modules: dict[str, Any] = {}


def _import_module_safely(module_name: str):
    """Try to import a module and return it, or None if not available."""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def __getattr__(name: str) -> Any:
    if name == "_MCP_AVAILABLE":
        return _import_module_safely("clarity_api.mcp_server") is not None
    if name == "_AGENT_AVAILABLE":
        return _import_module_safely("clarity_api.agent_server") is not None

    for module_name in OPTIONAL_MODULES:
        if module_name not in _loaded_optional_modules:
            module = _import_module_safely(module_name)
            if module is not None:
                _loaded_optional_modules[module_name] = module
                _expose_members(module)

        module = _loaded_optional_modules.get(module_name)
        if module is not None and hasattr(module, name):
            return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + __all__)
