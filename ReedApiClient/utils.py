from datetime import datetime
from typing import (Any, Callable, Coroutine, NewType, Optional, TypeVar, overload)
from urllib.parse import urlunparse

import httpx

import _model

REED_API_BASE_URL = "www.reed.co.uk"
DEFAULT_API_PATH = "api"
DEFAULT_VERSION_STRING = "1.0"
DEFAULT_PROTOCOL = "https"
JOB_SEARCH_PATH = "search"

UseSync = NewType("UseSync", bool)
UseAsync = NewType("UseAsync", bool)

# A generic type to represent the type a parser function should return
# This can be any type that inherits from _model.APIResponseBaseModel
# but may vary depending on the types passed into the function

# pylint: disable=invalid-name
TGenericApiResponse = TypeVar("TGenericApiResponse", bound="_model.APIResponseBaseModel")
#pylint: enable=invalid-name


def get_base_url(
    protocol: str = DEFAULT_PROTOCOL,
    netloc: str = REED_API_BASE_URL,
    port: Optional[int] = None,
    api_path: str = DEFAULT_API_PATH,
    version: str = DEFAULT_VERSION_STRING,
) -> str:
    """
    Build a base URL for the REED API.

    Args:
        protocol: The protocol to use for the URL. Defaults to https.
        netloc: The network location to use for the URL. Defaults to the REED API base URL.
        port: The port to use for the URL. Defaults to None.
        api_path: The API path to use for the URL. Defaults to the default API path.
        version: The version string to use for the URL. Defaults to the default version string.

    Returns:
        str: The constructed base URL.
    """
    if port:
        netloc = f"{netloc}:{port}"
    path = f"/{api_path}/{version}"

    url = urlunparse((protocol, netloc, path, "", "", ""))

    return url


def get_detail_url(job_id: int | str, base_url: Optional[str] = get_base_url()) -> str:
    # https://www.reed.co.uk/api/1.0/jobs/132
    _url = f"{base_url}/jobs/{job_id}"
    return _url


def get_search_url(base_url: Optional[str] = get_base_url()) -> str:
    # https://www.reed.co.uk/api/1.0/search
    _url = f"{base_url}/{JOB_SEARCH_PATH}"

    return _url


def parse_date_string(date_string: str) -> Optional[datetime]:
    """
    Parse a date string from the REED API into a datetime object.

    Args:
        date_string (str): The date string from the REED API

    Returns:
        datetime: The parsed datetime object
    """
    _date = None
    try:
        # _date = datetime.strptime(date_string, "%Y-%m-%d")
        _date = datetime.strptime(date_string, "%d/%m/%Y")
    except BaseException:

        # TODO: Add logging
        pass
    return _date


@overload
def parse_response(
    response: httpx.Response,
    parse_func: Callable[[httpx.Response], TGenericApiResponse],
) -> TGenericApiResponse:
    ...


@overload
def parse_response(
    response: Coroutine[Any, Any, httpx.Response],
    parse_func: Callable[[httpx.Response], TGenericApiResponse],
) -> Coroutine[Any, Any, TGenericApiResponse]:
    ...


def parse_response(
    response: httpx.Response | Coroutine[Any, Any, httpx.Response],
    parse_func: Callable[[httpx.Response], TGenericApiResponse],
) -> TGenericApiResponse | Coroutine[Any, Any, TGenericApiResponse]:
    if isinstance(response, Coroutine):
        return modify_result_async(response, parse_func)

    if isinstance(response, httpx.Response):
        return parse_func(response)

    raise TypeError("response must be a httpx.Response object")


def check_response(response: httpx.Response) -> httpx.Response:
    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}")
    return response


async def modify_result_async(
        coro, result_parser: Callable[[httpx.Response],
                                      TGenericApiResponse]) -> TGenericApiResponse:

    coro_result: httpx.Response = await coro
    parsed_result = result_parser(coro_result)
    return parsed_result


def job_search_response_parser(response: httpx.Response) -> "_model.JobSearchResponse":
    models = [_model.JobSearchPartialJob(**job) for job in response.json()["results"]]
    return _model.JobSearchResponse(jobs=models,
                                    raw_response=response,
                                    raw_request=response.request)


def job_detail_response_parser(response: httpx.Response) -> "_model.JobDetailResponse":
    raw_response_data = response.json()

    data = _model.JobDetail(**raw_response_data)
    result_model = _model.JobDetailResponse(job=data,
                                            raw_response=response,
                                            raw_request=response.request)
    return result_model
