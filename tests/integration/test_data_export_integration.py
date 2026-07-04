"""End-to-end integration tests for the Clarity data-export path.

Exercises the full ``clarity_insights`` MCP tool -> ``get_client`` -> Clarity
client wiring (HTTP mocked via the shared conftest fixtures), covering
``CONCEPT:CY-OS.governance.data-export-live-insights`` (Data Export / Live Insights). Test names intentionally
mirror the README feature headings so documented capabilities stay covered.
"""

import json

import pytest

from clarity_api.auth import get_client
from clarity_api.mcp.mcp_insights import _serialize


@pytest.fixture
def export_client():
    """A configured Clarity client built through the auth factory."""
    return get_client(
        instance="https://www.clarity.ms", token="mock_token", verify=False
    )


@pytest.mark.concept("CY-OS.governance.data-export-live-insights")
def test_integration_available_mcp_tools_data_export_dimensions(export_client):
    """Integration: data export with multiple dimension breakdowns returns data."""
    response = export_client.get_data_export(
        number_of_days=3, dimension_1="OS", dimension_2="Country"
    )
    payload = _serialize(response)
    assert payload["status_code"] == 200
    assert "data" in payload["data"]
    metrics = payload["data"]["data"]
    assert metrics[0]["metricName"] == "Traffic"


@pytest.mark.concept("CY-OS.governance.data-export-live-insights")
def test_integration_usage_python_client_configuration(export_client):
    """Integration: the documented Python-client usage flow works end to end."""
    response = export_client.get_data_export(number_of_days=1)
    body = response.json()
    assert response.status_code == 200
    info = body["data"][0]["information"][0]
    assert info["OS"] == "Android"
    assert int(info["totalSessionCount"]) > 0


@pytest.mark.concept("CY-OS.governance.data-export-live-insights")
def test_integration_serialize_wraps_response_for_transport():
    """Integration: ``_serialize`` produces an MCP-safe status/data envelope."""

    class _Resp:
        status_code = 200

        def json(self):
            return {"ok": True}

    out = _serialize(_Resp())
    assert out == {"status_code": 200, "data": {"ok": True}}
    # Round-trips through JSON without error (transport-safe).
    assert json.loads(json.dumps(out))["status_code"] == 200
