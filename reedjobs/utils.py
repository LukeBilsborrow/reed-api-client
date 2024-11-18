from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union
from urllib.parse import urlunparse

import httpx

from reedjobs import _model, _types

REED_API_BASE_URL = "www.reed.co.uk"
DEFAULT_API_PATH = "api"
DEFAULT_VERSION_STRING = "1.0"
DEFAULT_PROTOCOL = "https"
JOB_SEARCH_PATH = "search"

# A generic type to represent the type a parser function should return
# This can be any type that inherits from _model.APIResponseBaseModel
# but may vary depending on the types passed into the function

# pylint: disable=invalid-name
TGenericApiResponse = TypeVar("TGenericApiResponse", bound="_model.APIResponseBaseModel")
# pylint: enable=invalid-name


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


def get_detail_url(job_id: Union[int, str], base_url: Optional[str] = get_base_url()) -> str:
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
        _date = try_wrapper(lambda: datetime.strptime(date_string, "%d/%m/%Y"))

        if not _date:
            _date = try_wrapper(lambda: datetime.strptime(date_string, "%Y-%m-%d"))

    except BaseException:  # pylint: disable=broad-except

        # TODO: Add logging
        pass
    return _date


def handle_response(
    response: _types.PossiblyAsyncResponse,
    response_parser: Callable[[httpx.Response, Union[dict, None]], TGenericApiResponse],
) -> Union[TGenericApiResponse, Coroutine[Any, Any, TGenericApiResponse]]:

    if isinstance(response, Coroutine):
        return _handle_response_async(response, response_parser)

    return _handle_response(response, response_parser)


# this method is responble for parsing the response and returning the parsed result
def _handle_response(
    response: httpx.Response, response_parser: Callable[[httpx.Response, Union[dict, None]],
                                                        TGenericApiResponse]
) -> TGenericApiResponse:
    """
    Parse a response from the REED API and return the parsed result.

    Args:
        response: The response from the REED API
        result_parser: A function to parse the response

    Returns:
        Optional[TGenericApiResponse]: The parsed result, or None if the request failed
    """

    json_result = get_response_json(response)

    # it is up to the response parser to handle the case where the input data is None
    parsed_result = response_parser(response, json_result)
    return parsed_result


async def _handle_response_async(
    coro: Coroutine[Any, Any,
                    httpx.Response], result_parser: Callable[[httpx.Response, Union[dict, None]],
                                                             TGenericApiResponse]
) -> TGenericApiResponse:
    """
    An async wrapper for _handle_response

    This method simply wraps the _handle_response method in an async context
    and awaits the result of the coroutine passed in before passing it to the
    _handle_response method

    Args:
        coro: The coroutine to await
        result_parser: The function to parse the response with

    Returns:
        The parsed result of the response, or None
    """
    coro_result: httpx.Response = await coro
    parsed_result = _handle_response(coro_result, result_parser)
    return parsed_result


def try_wrapper(func: Callable) -> Any:
    """
    Executes a given function and returns its result, or None if an exception occurs.

    Args:
        func (Callable): The function to execute.

    Returns:
        Any: The result of the function if successful, otherwise None if an exception occurs.
    """
    try:
        return func()
    except BaseException:  # pylint: disable=broad-except
        return None


def get_response_json(response: httpx.Response) -> Optional[dict]:

    try:
        response.raise_for_status()
        data = response.json()

    except BaseException:  # pylint: disable=broad-except
        # TODO: Add logging
        data = None
    return data


def job_search_response_parser(response: httpx.Response,
                               response_data: Optional[dict]) -> _model.JobSearchResponse:

    if not response_data:
        return _model.JobSearchResponse(raw_request=response.request,
                                        raw_response=response,
                                        success=False)

    models = [_model.JobSearchPartialJob(**job) for job in response_data["results"]]
    return _model.JobSearchResponse(jobs=models,
                                    raw_response=response,
                                    raw_request=response.request)


def job_detail_response_parser(response: httpx.Response,
                               response_data: Union[dict, None]) -> _model.JobDetailResponse:
    if not response_data:
        data = None
    else:
        data = _model.JobDetail(**response_data)
    result_model = _model.JobDetailResponse(job=data,
                                            raw_response=response,
                                            raw_request=response.request)
    return result_model


def to_camel_case(snake_str):
    snake_str = snake_str.lower()
    new_str = "".join(x.capitalize() for x in snake_str.split("_"))
    new_str = new_str[0].lower() + new_str[1:]
    return new_str
