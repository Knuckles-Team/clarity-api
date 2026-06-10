"""Tests for the auth.get_client dependency factory."""

import importlib.util

import pytest

# get_client uses agent_utilities.mcp.delegated_auth, available in agent-utilities>=0.47.
try:
    _HAS_DELEGATED_AUTH = (
        importlib.util.find_spec("agent_utilities.mcp.delegated_auth") is not None
    )
except ModuleNotFoundError:
    _HAS_DELEGATED_AUTH = False
pytestmark = pytest.mark.skipif(
    not _HAS_DELEGATED_AUTH,
    reason="agent-utilities>=0.47 (agent_utilities.mcp.delegated_auth) not installed",
)


def test_get_client_returns_api(monkeypatch):
    monkeypatch.setenv("CLARITY_URL", "https://www.clarity.ms")
    monkeypatch.setenv("CLARITY_TOKEN", "mock_token")
    monkeypatch.setenv("CLARITY_SSL_VERIFY", "False")

    from clarity_api.api_client import Api
    from clarity_api.auth import get_client

    client = get_client(
        instance="https://www.clarity.ms", token="mock_token", verify=False
    )
    assert isinstance(client, Api)


def test_get_client_data_export(monkeypatch):
    monkeypatch.setenv("CLARITY_TOKEN", "mock_token")
    from clarity_api.auth import get_client

    client = get_client(
        instance="https://www.clarity.ms", token="mock_token", verify=False
    )
    response = client.get_data_export(number_of_days=1)
    assert response.status_code == 200
