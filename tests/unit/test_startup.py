"""Startup / import-surface tests for the MCP and agent entry points.

Covers ``CONCEPT:CY-OS.governance.package-server-bootstrap`` (Package & Server Bootstrap).
"""

import importlib

import pytest


@pytest.mark.concept("CY-OS.governance.package-server-bootstrap")
def test_concept_cla_005_mcp_server_imports():
    """CLA-005: the MCP server module exposes its callable entry points."""
    srv = importlib.import_module("clarity_api.mcp_server")
    assert callable(srv.mcp_server)
    assert callable(srv.get_mcp_instance)
    assert isinstance(srv.__version__, str)


@pytest.mark.concept("CY-OS.governance.package-server-bootstrap")
def test_concept_cla_005_agent_server_imports():
    """CLA-005: the agent server module exposes its callable entry point."""
    srv = importlib.import_module("clarity_api.agent_server")
    assert callable(srv.agent_server)
    assert isinstance(srv.__version__, str)


@pytest.mark.concept("CY-OS.governance.package-server-bootstrap")
def test_concept_cla_005_versions_match_package():
    """CLA-005: package, MCP, and agent version strings stay in lock-step."""
    import clarity_api

    mcp = importlib.import_module("clarity_api.mcp_server")
    agent = importlib.import_module("clarity_api.agent_server")
    assert clarity_api.__version__ == mcp.__version__ == agent.__version__
