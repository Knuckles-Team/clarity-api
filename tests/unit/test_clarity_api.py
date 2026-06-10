"""Smoke test that the public package imports and exposes the Api class.

Covers ``CONCEPT:CLA-001`` (Data Export / Live Insights) via the public surface.
"""

import pytest


@pytest.mark.concept("CLA-001")
def test_concept_cla_001_package_exposes_api():
    """CLA-001: the top-level package re-exports the ``Api`` class."""
    import clarity_api

    assert hasattr(clarity_api, "Api")
    assert clarity_api.Api.__name__ == "Api"


@pytest.mark.concept("CLA-001")
def test_concept_cla_001_get_data_export_via_public_api():
    """CLA-001: the public ``Api`` performs a data export end to end."""
    import clarity_api

    client = clarity_api.Api(
        url="https://www.clarity.ms", token="mock_token", verify=False
    )
    response = client.get_data_export(number_of_days=3, dimension_1="OS")
    assert response.status_code == 200
    assert "data" in response.json()
