from datetime import date
from typing import Optional

import httpx
from pydantic import BaseModel, Field, field_validator

import utils


class APIResponseBaseModel(BaseModel):
    raw_request: Optional[httpx.Request]
    raw_response: Optional[httpx.Response]

    class Config:  # pylint: disable=too-few-public-methods
        arbitrary_types_allowed = True


class JobSearchPartialJob(BaseModel):
    jobId: int
    employerId: int
    employerName: str
    employerProfileId: Optional[int]
    employerProfileName: Optional[str]
    jobTitle: str
    locationName: str
    minimumSalary: Optional[float]
    maximumSalary: Optional[float]
    currency: Optional[str]
    expirationDate: Optional[date]
    postedDate: Optional[date] = Field(alias="date")
    jobDescription: str
    applications: int
    jobUrl: str

    validate_date_fields = field_validator("expirationDate", "postedDate",
                                           mode="before")(utils.parse_date_string)


class JobSearchResponse(APIResponseBaseModel):

    jobs: list[JobSearchPartialJob]


class JobDetail(BaseModel):
    employerId: Optional[int]
    employerName: str
    jobId: int
    jobTitle: str
    locationName: str
    minimumSalary: Optional[float]
    maximumSalary: Optional[float]
    yearlyMinimumSalary: Optional[float]
    yearlyMaximumSalary: Optional[float]
    currency: Optional[str]

    salaryType: str
    salary: str
    postedDate: Optional[date] = Field(alias="datePosted")
    expirationDate: Optional[date]
    externalUrl: str
    jobUrl: str
    partTime: bool
    fullTime: bool
    contractType: str
    jobDescription: str
    applicationCount: int

    validate_date_fields = field_validator("expirationDate", "postedDate",
                                           mode="before")(utils.parse_date_string)


class JobDetailResponse(APIResponseBaseModel):
    job: JobDetail


class JobSearchRequest(BaseModel):
    """
    A pydantic model for the request body
    """

    employerId: Optional[int] = None
    employerProfileId: Optional[int] = None
    keywords: Optional[str] = None
    locationName: Optional[str] = None
    distanceFromLocation: Optional[int] = 10
    permanent: Optional[bool] = None
    contract: Optional[bool] = None
    temp: Optional[bool] = None
    partTime: Optional[bool] = None
    fullTime: Optional[bool] = None
    minimumSalary: Optional[int] = None
    maximumSalary: Optional[int] = None
    postedByRecruitmentAgency: Optional[bool] = None
    postedByDirectEmployer: Optional[bool] = None
    graduate: Optional[bool] = None
    resultsToTake: Optional[int] = 100
    resultsToSkip: Optional[int] = 0

    @field_validator("distanceFromLocation")
    # pylint: disable=no-self-argument, invalid-name
    def distanceFromLocation_cannot_be_negative(cls, v):
        # pylint: enable=no-self-argument, invalid-name

        if v < 0:
            raise ValueError("distanceFromLocation must be a positive number")
        return v

    @field_validator("resultsToTake")
    # pylint: disable=no-self-argument, invalid-name
    def resultsToTake_cannot_be_too_large(cls, v):
        # pylint: enable=no-self-argument, invalid-name

        if v > 100:
            raise ValueError("resultsToTake must be less than or equal to 100")
        return v

    @field_validator("resultsToSkip")
    # pylint: disable=no-self-argument, invalid-name
    def resultsToSkip_cannot_be_negative(cls, v):
        # pylint: enable=no-self-argument, invalid-name

        if v < 0:
            raise ValueError("resultsToSkip must be a positive number")
        return v


class JobDetailRequest(JobSearchRequest):
    # pylint: disable=too-few-public-methods
    jobId: int
