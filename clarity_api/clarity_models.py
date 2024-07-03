#!/usr/bin/python
# coding: utf-8
import logging

from typing import Union, Dict, Optional, Any, List
from pydantic import (
    BaseModel,
    ConfigDict,
    AliasChoices,
    Field,
    field_validator,
)

try:
    from clarity_api.decorators import require_auth
except ModuleNotFoundError:
    pass
try:
    from clarity_api.exceptions import (
        AuthError,
        UnauthorizedError,
        ParameterError,
        MissingParameterError,
    )
except ModuleNotFoundError:
    pass

logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


class InputModel(BaseModel):
    """
    Pydantic model representing information about a branch.

    Attributes:
        numOfDays (Union[int, str]): The number of days to return.
        dimension1 (str, optional): The first dimension parameters.
        dimension2 (str, optional): The second dimension parameters.
        dimension3 (str, optional): The third dimension parameters.
        api_parameters (str): Additional API parameters for the group.

    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    numOfDays: Optional[Union[int, str]] = Field(
        description="Number of days to save",
        validation_alias=AliasChoices("numOfDays", "number_of_days"),
        default=None,
    )
    dimension1: Optional[str] = Field(
        description="Dimension 1",
        validation_alias=AliasChoices("dimension1", "dimension_1"),
        default=None,
    )
    dimension2: Optional[str] = Field(
        description="Dimension 2",
        validation_alias=AliasChoices("dimension2", "dimension_2"),
        default=None,
    )
    dimension3: Optional[str] = Field(
        description="Dimension 3",
        validation_alias=AliasChoices("dimension3", "dimension_3"),
        default=None,
    )
    api_parameters: Optional[Dict] = Field(description="API Parameters", default=None)

    def model_post_init(self, __context):
        """
        Build the API parameters
        """
        self.api_parameters = {}
        if self.numOfDays:
            self.api_parameters["numOfDays"] = self.numOfDays
        if self.dimension1:
            self.api_parameters["dimension1"] = self.dimension1
        if self.dimension2:
            self.api_parameters["dimension2"] = self.dimension2
        if self.dimension3:
            self.api_parameters["dimension3"] = self.dimension3

    @field_validator("numOfDays", mode="before")
    def validate_number_of_days(cls, v):
        """
        Validate the 'number_of_days' parameter to ensure it is a valid integer.

        Args:
        - v: The value of 'number_of_days'.

        Returns:
        - int: The validated 'number_of_days'.

        Raises:
        - ParameterError: If 'number_of_days' is not a valid integer.
        """
        try:
            v = int(v)
        except Exception as e:
            raise e
        return v

    @field_validator("dimension1", "dimension2", "dimension3", mode="before")
    def validate_dimensions(cls, v):
        """
        Validate the 'dimensions' parameter to ensure it is a valid option.

        Args:
        - v: The value of 'dimensions'.

        Returns:
        - str: The validated 'dimensions'.

        Raises:
        - ParameterError: If 'dimensions' is not a valid option.
        """
        if v:
            valid_dimensions = {
                "browser": "Browser",
                "device": "Device",
                "country": "Country",
                "os": "OS",
                "source": "Source",
                "medium": "Medium",
                "campaign": "Campaign",
                "channel": "Channel",
                "url": "URL",
            }
            try:
                return valid_dimensions[v.lower()]
            except KeyError:
                raise ValueError("Invalid dimension")


class Information(BaseModel):
    model_config = ConfigDict(extra="allow")
    totalSessionCount: str = Field(
        default=None, description="The total number of sessions."
    )
    totalBotSessionCount: str = Field(
        default=None, description="The total number of bot sessions."
    )
    distantUserCount: str = Field(default=None, description="The distant user count.")
    PagesPerSessionPercentage: float = Field(
        default=None, description="The pages per session percentage."
    )
    OS: str = Field(default=None, description="The operating system.")


class Metric(BaseModel):
    model_config = ConfigDict(extra="allow")
    metricName: str = Field(
        default=None, description="The name of the returned metric."
    )
    information: List[Information] = Field(
        default=None, description="Result containing available responses."
    )


class Response(BaseModel):
    data: Optional[List[Metric]] = Field(default=None, description="Metrics returned.")
    error: Optional[Any] = Field(default=None, description="Response error code")
    status_code: Union[str, int] = Field(
        default=None, description="Response status code"
    )
    json_output: Optional[Union[List, Dict]] = Field(
        default=None, description="Response JSON data"
    )
    raw_output: Optional[bytes] = Field(default=None, description="Response Raw bytes")
