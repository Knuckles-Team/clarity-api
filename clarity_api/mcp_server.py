#!/usr/bin/python
import warnings

from fastmcp import FastMCP

# Filter RequestsDependencyWarning early to prevent log spam
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        from requests.exceptions import RequestsDependencyWarning

        warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
    except ImportError:
        pass

# General urllib3/chardet mismatch warnings
warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
warnings.filterwarnings("ignore", message=".*urllib3.*or charset_normalizer.*")

import logging
import os
import sys
from typing import Any

from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import create_mcp_server
from dotenv import find_dotenv, load_dotenv
from fastmcp.utilities.logging import get_logger

from clarity_api.mcp import register_insights_tools

__version__ = "1.0.0"
print(f"Clarity MCP v{__version__}", file=sys.stderr)

logger = get_logger(name="mcp_server")
logger.setLevel(logging.DEBUG)

DEFAULT_CLARITY_SSL_VERIFY = to_boolean(string=os.getenv("CLARITY_SSL_VERIFY", "True"))
DEFAULT_CLARITY_URL = os.getenv("CLARITY_URL", "https://www.clarity.ms")
DEFAULT_CLARITY_TOKEN = os.getenv("CLARITY_TOKEN", None)


def get_mcp_instance() -> tuple[Any, Any, Any, Any]:
    """Initialize and return the Clarity MCP instance, args, and middlewares."""
    load_dotenv(find_dotenv())
    os.environ["FASTMCP_LOG_LEVEL"] = "ERROR"
    os.environ["TERM"] = "dumb"
    os.environ["NO_COLOR"] = "1"

    args, mcp, middlewares = create_mcp_server(
        name="Clarity",
        version=__version__,
        instructions=(
            "Microsoft Clarity API MCP Server - Export dashboard data and live "
            "insights broken down by up to three dimensions."
        ),
    )

    DEFAULT_INSIGHTSTOOL = to_boolean(os.getenv("INSIGHTSTOOL", "True"))
    if DEFAULT_INSIGHTSTOOL:
        register_insights_tools(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)

    registered_tags: list[str] = []
    return mcp, args, middlewares, registered_tags


def mcp_server() -> None:
    mcp, args, middlewares, registered_tags = get_mcp_instance()
    print(f"{'clarity-api'} MCP v{__version__}", file=sys.stderr)
    print("\nStarting MCP Server", file=sys.stderr)
    print(f"  Transport: {args.transport.upper()}", file=sys.stderr)
    print(f"  Auth: {args.auth_type}", file=sys.stderr)
    print(f"  Dynamic Tags Loaded: {len(set(registered_tags))}", file=sys.stderr)

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.error("Invalid transport", extra={"transport": args.transport})
        sys.exit(1)


if __name__ == "__main__":
    mcp_server()
