"""Startup / import-surface tests for the MCP and agent entry points."""

import importlib


def test_mcp_server_imports():
    srv = importlib.import_module("clarity_api.mcp_server")
    assert callable(srv.mcp_server)
    assert callable(srv.get_mcp_instance)
    assert isinstance(srv.__version__, str)


def test_agent_server_imports():
    srv = importlib.import_module("clarity_api.agent_server")
    assert callable(srv.agent_server)
    assert isinstance(srv.__version__, str)


def test_versions_match_package():
    import clarity_api

    mcp = importlib.import_module("clarity_api.mcp_server")
    agent = importlib.import_module("clarity_api.agent_server")
    assert clarity_api.__version__ == mcp.__version__ == agent.__version__
