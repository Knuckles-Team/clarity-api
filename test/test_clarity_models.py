#!/usr/bin/python
# coding: utf-8

import os
import sys

import pytest
from conftest import reason

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    import clarity_api
    from clarity_api.clarity_models import (
        InputModel,
        Response,
    )

except ImportError:
    skip = True
    raise ("ERROR IMPORTING", ImportError)
else:
    skip = False

reason = "do not run on MacOS or windows OR dependency is not installed OR " + reason


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_input_model():
    num_of_days = 2
    dimension1 = "OS"
    dimension2 = "Country"
    dimension_3 = "channel"
    input_model = InputModel(
        number_of_days=num_of_days,
        dimension_1=dimension1,
        dimension_2=dimension2,
        dimension_3=dimension_3,
    )
    assert input_model.numOfDays == num_of_days
    assert input_model.dimension1 == dimension1
    assert input_model.dimension2 == dimension2
    assert input_model.dimension3 == dimension_3.capitalize()
    assert input_model.api_parameters == {
        "numOfDays": num_of_days,
        "dimension1": dimension1,
        "dimension2": dimension2,
        "dimension3": dimension_3.capitalize(),
    }


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_response_model():
    data = [
        {
            "metricName": "Traffic",
            "information": [
                {
                    "totalSessionCount": "9554",
                    "totalBotSessionCount": "8369",
                    "distantUserCount": "189733",
                    "PagesPerSessionPercentage": 1.0931,
                    "OS": "Other",
                },
                {
                    "totalSessionCount": "291942",
                    "totalBotSessionCount": "31076",
                    "distantUserCount": "212836",
                    "PagesPerSessionPercentage": 2.2609,
                    "OS": "Android",
                },
            ],
        }
    ]
    response = Response(data=data)
    assert response.data[0].information[0].model_dump() == data[0]["information"][0]


if __name__ == "__main__":
    test_input_model()
    test_response_model()
