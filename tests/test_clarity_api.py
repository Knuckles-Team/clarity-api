"""Smoke test that the public package imports and exposes the Api class."""


def test_package_exposes_api():
    import clarity_api

    assert hasattr(clarity_api, "Api")


def test_get_data_export_via_public_api():
    import clarity_api

    client = clarity_api.Api(
        url="https://www.clarity.ms", token="mock_token", verify=False
    )
    response = client.get_data_export(number_of_days=3, dimension_1="OS")
    assert response.status_code == 200
