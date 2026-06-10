"""Tests for the Clarity Api client facade and backward-compat shim.

Covers ``CONCEPT:CLA-001`` (Data Export / Live Insights) and
``CONCEPT:CLA-004`` (REST Base Client).
"""

import pytest

from clarity_api.api_client import Api


@pytest.fixture
def client() -> Api:
    """A credential-validated Clarity ``Api`` client (HTTP mocked via conftest)."""
    return Api(url="https://www.clarity.ms", token="mock_token", verify=False)


@pytest.mark.concept("CLA-004")
def test_api_facade_importable():
    """The facade ``Api`` symbol is importable from the canonical module."""
    assert Api.__name__ == "Api"
    assert hasattr(Api, "get_data_export")


@pytest.mark.concept("CLA-004")
def test_backward_compat_import():
    """The original ``clarity_api.clarity_api`` import path must keep working."""
    from clarity_api.api_client import Api as FacadeApi
    from clarity_api.clarity_api import Api as LegacyApi

    assert LegacyApi is FacadeApi


@pytest.mark.concept("CLA-001")
def test_concept_cla_001_construction_and_data_export(client):
    """CLA-001: constructing the client and exporting data returns metrics."""
    response = client.get_data_export(number_of_days=2, dimension_1="OS")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert body["data"][0]["metricName"] == "Traffic"


@pytest.mark.concept("CLA-001")
@pytest.mark.parametrize(
    "params",
    [
        {"number_of_days": 1},
        {"number_of_days": 2, "dimension_1": "OS"},
        {"number_of_days": 3, "dimension_1": "Browser", "dimension_2": "Country"},
    ],
)
def test_concept_cla_001_data_export_parametrized(client, params):
    """CLA-001: data export succeeds across valid day/dimension combinations."""
    response = client.get_data_export(**params)
    assert response.status_code == 200


@pytest.mark.concept("CLA-001")
def test_concept_cla_001_data_export_with_api_parameters_dict(client):
    """CLA-001: a pre-built ``api_parameters`` dict bypasses kwarg modeling."""
    response = client.get_data_export(api_parameters={"numOfDays": 1})
    assert response.status_code == 200


@pytest.mark.concept("CLA-004")
def test_concept_cla_004_api_request_helper(client):
    """CLA-004: the base ``api_request`` helper issues arbitrary REST calls."""
    response = client.api_request(method="GET", endpoint="/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
