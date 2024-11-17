from __future__ import annotations

from datetime import date
from typing import Union

import httpx
from pydantic import BaseModel, Field, field_validator

from reedjobs import utils


class APIResponseBaseModel(BaseModel):
    raw_request: httpx.Request
    raw_response: httpx.Response
    success: bool = True

    class Config:  # pylint: disable=too-few-public-methods
        arbitrary_types_allowed = True


class JobSearchRequest(BaseModel):
    """
    A pydantic model for the request body
    """

    employerId: Union[int, None]
    employerProfileId: Union[int, None]
    keywords: Union[str, None]
    locationName: Union[str, None]
    distanceFromLocation: Union[int, None] = 10
    permanent: Union[bool, None]
    contract: Union[bool, None]
    temp: Union[bool, None]
    partTime: Union[bool, None]
    fullTime: Union[bool, None]
    minimumSalary: Union[int, None]
    maximumSalary: Union[int, None]
    postedByRecruitmentAgency: Union[bool, None]
    postedByDirectEmployer: Union[bool, None]
    graduate: Union[bool, None]
    resultsToTake: Union[int, None] = 100
    resultsToSkip: Union[int, None] = 0

    @field_validator("distanceFromLocation")
    # pylint: disable=no-self-argument, invalid-name
    def distanceFromLocation_cannot_be_negative(cls, v):
        # pylint: enable=no-self-argument, invalid-name

        if v is not None and v < 0:
            raise ValueError("distanceFromLocation must be a positive number")
        return v

    @field_validator("resultsToTake")
    # pylint: disable=no-self-argument, invalid-name
    def resultsToTake_cannot_be_too_large(cls, v):
        # pylint: enable=no-self-argument, invalid-name

        if v is not None and v > 100:
            raise ValueError("resultsToTake must be less than or equal to 100")
        return v

    @field_validator("resultsToSkip")
    # pylint: disable=no-self-argument, invalid-name
    def resultsToSkip_cannot_be_negative(cls, v):
        # pylint: enable=no-self-argument, invalid-name

        if v is not None and v < 0:
            raise ValueError("resultsToSkip must be a positive number")
        return v


class JobDetailRequest(JobSearchRequest):
    # pylint: disable=too-few-public-methods
    jobId: int


class JobSearchPartialJob(BaseModel):
    jobId: int
    employerId: int
    employerName: str
    employerProfileId: Union[int, None]
    employerProfileName: Union[str, None]
    jobTitle: str
    locationName: str
    minimumSalary: Union[float, None]
    maximumSalary: Union[float, None]
    currency: Union[str, None]
    expirationDate: Union[date, None]
    postedDate: Union[date, None] = Field(alias="date")
    jobDescription: str
    applications: int
    jobUrl: str

    validate_date_fields = field_validator("expirationDate", "postedDate",
                                           mode="before")(utils.parse_date_string)


class JobDetail(BaseModel):
    employerId: Union[int, None]
    employerName: str
    jobId: int
    jobTitle: str
    locationName: str
    minimumSalary: Union[float, None]
    maximumSalary: Union[float, None]
    yearlyMinimumSalary: Union[float, None]
    yearlyMaximumSalary: Union[float, None]
    currency: Union[str, None]
    salaryType: Union[str, None]
    salary: Union[str, None]
    postedDate: Union[date, None] = Field(alias="datePosted")
    expirationDate: Union[date, None]
    externalUrl: Union[str, None]
    jobUrl: str
    partTime: Union[bool, None]
    fullTime: Union[bool, None]
    contractType: Union[str, None]
    jobDescription: str
    applicationCount: Union[int, None]

    validate_date_fields = field_validator("expirationDate", "postedDate",
                                           mode="before")(utils.parse_date_string)


class JobSearchResponse(APIResponseBaseModel):

    jobs: Union[list[JobSearchPartialJob], None] = None


class JobDetailResponse(APIResponseBaseModel):
    job: Union[JobDetail, None]
