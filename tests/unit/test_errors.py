"""Negative / error-path tests for the Clarity REST base client.

Covers ``CONCEPT:CY-OS.governance.rest-base-client-owns`` (REST Base Client) credential-validation failures and
``CONCEPT:CY-OS.governance.input-validation-parameter-modeling`` (Input Validation) rejection of bad parameters.
"""

from unittest.mock import patch

import pytest
from pydantic import ValidationError
from requests import Response

from clarity_api.api_client import Api
from clarity_api.clarity_models import InputModel
from clarity_api.exceptions import (
    AuthError,
    MissingParameterError,
    ParameterError,
    UnauthorizedError,
)


def _response_with_status(status_code: int) -> Response:
    resp = Response()
    resp.status_code = status_code
    resp._content = b"{}"
    return resp


@pytest.mark.concept("CY-OS.governance.rest-base-client-owns")
@pytest.mark.parametrize(
    ("status_code", "expected_exc"),
    [
        (403, UnauthorizedError),
        (401, AuthError),
        (404, ParameterError),
    ],
)
def test_concept_cla_004_credential_validation_errors(status_code, expected_exc):
    """CLA-004: validation HTTP errors raise the mapped domain exception."""
    with patch(
        "requests.Session.get",
        return_value=_response_with_status(status_code),
    ):
        with pytest.raises(expected_exc):
            Api(url="https://www.clarity.ms", token="mock_token", verify=False)


@pytest.mark.concept("CY-OS.governance.rest-base-client-owns")
def test_concept_cla_004_missing_token_raises():
    """CLA-004: omitting the token fails fast with MissingParameterError."""
    with pytest.raises(MissingParameterError):
        Api(url="https://www.clarity.ms", token=None, verify=False)


@pytest.mark.concept("CY-OS.governance.rest-base-client-owns")
def test_concept_cla_004_missing_url_raises():
    """CLA-004: omitting the URL fails fast with MissingParameterError."""
    with pytest.raises(MissingParameterError):
        Api(url=None, token="mock_token", verify=False)


@pytest.mark.concept("CY-OS.governance.input-validation-parameter-modeling")
@pytest.mark.parametrize("bad_days", ["not-a-number", "abc"])
def test_concept_cla_003_invalid_days_rejected(bad_days):
    """CLA-003: a non-integer day count is rejected during validation."""
    with pytest.raises(ValidationError):
        InputModel(number_of_days=bad_days)  # type: ignore[call-arg]


@pytest.mark.concept("CY-OS.governance.input-validation-parameter-modeling")
def test_concept_cla_003_invalid_dimension_rejected():
    """CLA-003: an unknown dimension value raises a validation error."""
    with pytest.raises(ValidationError):
        InputModel(number_of_days=1, dimension_1="NotARealDimension")  # type: ignore[call-arg]
