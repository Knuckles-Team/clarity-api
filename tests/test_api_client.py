"""Tests for the Clarity Api client facade and backward-compat shim."""


def test_api_facade_importable():
    from clarity_api.api_client import Api

    assert Api is not None


def test_backward_compat_import():
    """The original import path must keep working."""
    from clarity_api.clarity_api import Api as LegacyApi
    from clarity_api.api_client import Api as FacadeApi

    assert LegacyApi is FacadeApi


def test_api_construction_and_data_export():
    """Constructing the client validates creds (mocked) and get_data_export works."""
    from clarity_api.api_client import Api

    client = Api(url="https://www.clarity.ms", token="mock_token", verify=False)
    response = client.get_data_export(number_of_days=2, dimension_1="OS")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body


def test_data_export_with_api_parameters_dict():
    from clarity_api.api_client import Api

    client = Api(url="https://www.clarity.ms", token="mock_token", verify=False)
    response = client.get_data_export(api_parameters={"numOfDays": 1})
    assert response.status_code == 200


def test_api_request_helper():
    from clarity_api.api_client import Api

    client = Api(url="https://www.clarity.ms", token="mock_token", verify=False)
    response = client.api_request(method="GET", endpoint="/projects")
    assert response.status_code == 200
