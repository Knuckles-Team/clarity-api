"""Tests for the dependency-injected ``InsightsService`` use-case layer.

Covers ``CONCEPT:CLA-001`` (Data Export / Live Insights) at the service seam.
"""

import pytest

from clarity_api.api_client import Api
from clarity_api.mcp.mcp_insights import _serialize
from clarity_api.services import InsightsService


@pytest.fixture
def service() -> InsightsService:
    """An ``InsightsService`` wired to a mocked client and the real serializer."""
    client = Api(url="https://www.clarity.ms", token="mock_token", verify=False)
    return InsightsService(client=client, serializer=_serialize)


@pytest.mark.concept("CLA-001")
def test_concept_cla_001_service_returns_serialized_payload(service):
    """CLA-001: the service returns a status/data envelope from the client."""
    payload = service.get_data_export(number_of_days=2, dimension_1="OS")
    assert payload["status_code"] == 200
    assert "data" in payload["data"]


@pytest.mark.concept("CLA-001")
def test_concept_cla_001_service_strips_none_kwargs():
    """CLA-001: ``None`` kwargs are dropped before reaching the client."""
    captured = {}

    class _FakeClient:
        def get_data_export(self, **kwargs):
            captured.update(kwargs)

            class _Resp:
                status_code = 200

                def json(self):
                    return {"data": []}

            return _Resp()

    service = InsightsService(client=_FakeClient(), serializer=_serialize)
    service.get_data_export(number_of_days=1, dimension_1=None, dimension_2=None)
    assert captured == {"number_of_days": 1}
