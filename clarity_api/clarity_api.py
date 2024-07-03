#!/usr/bin/python
# coding: utf-8

import requests
import urllib3
from typing import Union
from pydantic import ValidationError

try:
    from clarity_api.clarity_models import InputModel, Response
except ModuleNotFoundError:
    from clarity_models import InputModel, Response
try:
    from clarity_api.decorators import require_auth
except ModuleNotFoundError:
    from decorators import require_auth
try:
    from clarity_api.exceptions import (
        AuthError,
        UnauthorizedError,
        ParameterError,
        MissingParameterError,
    )
except ModuleNotFoundError:
    from exceptions import (
        AuthError,
        UnauthorizedError,
        ParameterError,
        MissingParameterError,
    )
try:
    from clarity_api.utils import process_response
except ModuleNotFoundError:
    from utils import process_response


class Api(object):

    def __init__(
        self,
        url: str = None,
        token: str = None,
        verify: bool = True,
    ):
        if url is None:
            raise MissingParameterError

        self._session = requests.Session()
        self.url = url
        self.headers = None
        self.verify = verify

        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if token:
            self.headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        else:
            raise MissingParameterError

        response = self._session.get(
            url=f"{self.url}/projects", headers=self.headers, verify=self.verify
        )

        if response.status_code == 403:
            print(f"Unauthorized Error: {response.content}")
            raise UnauthorizedError
        elif response.status_code == 401:
            print(f"Authentication Error: {response.content}")
            raise AuthError
        elif response.status_code == 404:
            print(f"Parameter Error: {response.content}")
            raise ParameterError

    ####################################################################################################################
    #                                              Data Export API                                                     #
    ####################################################################################################################
    @require_auth
    def get_data_export(self, **kwargs) -> Union[Response, requests.Response]:
        """
        Retrieve data insights for a project

        Args:
            **kwargs: Additional keyword arguments to initialize the BranchModel.

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid based on the BranchModel.
        """
        input_model = InputModel(**kwargs)
        try:
            response = self._session.get(
                url=f"{self.url}/export-data/api/v1/project-live-insights",
                params=input_model.api_parameters,
                headers=self.headers,
                verify=self.verify,
            )

        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        response = process_response(response=response)
        return response
