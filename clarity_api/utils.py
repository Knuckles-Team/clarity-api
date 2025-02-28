#!/usr/bin/python
# coding: utf-8
import logging
from typing import Union

import requests

try:
    from clarity_api.clarity_models import (
        Response,
    )
except ModuleNotFoundError:
    from clarity_models import (
        Response,
    )
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_response(response: requests.Response) -> Union[Response, requests.Response]:
    response_error = None
    try:
        response.raise_for_status()
    except Exception as response_error:
        logging.error(f"Response Error: {response_error}")
    status_code = response.status_code
    raw_output = response.content
    headers = response.headers
    try:
        response = response.json()
    except Exception as response_error:
        logging.error(f"JSON Conversion Error: {response_error}")
    try:
        response = Response(
            information=response,
            status_code=status_code,
            raw_output=raw_output,
            json_output=response,
            headers=headers,
            error=response_error,
        )
    except Exception as response_error:
        logging.error(f"Response Model Application Error: {response_error}")

    return response
