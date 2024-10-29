from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date
from utils import parse_date_string


class JobSearchRequest(BaseModel):
    """
    A pydantic model for the request body
    """

    employerId: int = None
    employerProfileId: int = None
    keywords: str = None
    locationName: str = None
    distanceFromLocation: int = 10
    permanent: bool = None
    contract: bool = None
    temp: bool = None
    partTime: bool = None
    fullTime: bool = None
    minimumSalary: int = None
    maximumSalary: int = None
    postedByRecruitmentAgency: bool = None
    postedByDirectEmployer: bool = None
    graduate: bool = None
    resultsToTake: int = 100
    resultsToSkip: int = 0

    @field_validator("distanceFromLocation")
    def distanceFromLocation_cannot_be_negative(cls, v):
        if v < 0:
            raise ValueError("distanceFromLocation must be a positive number")
        return v

    @field_validator("resultsToTake")
    def resultsToTake_cannot_be_too_large(cls, v):
        if v > 100:
            raise ValueError("resultsToTake must be less than or equal to 100")
        return v

    @field_validator("resultsToSkip")
    def resultsToSkip_cannot_be_negative(cls, v):
        if v < 0:
            raise ValueError("resultsToSkip must be a positive number")
        return v


class PartialJob(BaseModel):
    jobId: str
    employerId: int
    employerName: str
    employerProfileId: Optional[int]
    employerProfileName: Optional[str]
    jobTitle: str
    locationName: str
    minimumSalary: Optional[float]
    maximumSalary: Optional[float]
    currency: Optional[str]
    expirationDate: date
    postDate: date = Field(alias="date")
    jobDescription: str
    applications: int
    jobUrl: str

    validate_date_fields = field_validator("expirationDate", "postDate", mode="before")(
        parse_date_string
    )

    model_config = ConfigDict(coerce_numbers_to_str=True)


class JobSearchResponse(BaseModel):
    """
    A pydantic model for the response body
    """

    jobs: list[PartialJob]
