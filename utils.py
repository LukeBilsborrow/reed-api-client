from typing import Any, Callable, Coroutine, List, Optional
from urllib.parse import urlunparse
from datetime import datetime
import httpx
import _model

REED_API_BASE_URL = "www.reed.co.uk"
DEFAULT_API_PATH = "api"
DEFAULT_VERSION_STRING = "1.0"
DEFAULT_PROTOCOL = "https"


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

def get_detail_url(job_id:int|str, base_url:Optional[str] = get_base_url()) -> str:
    # https://www.reed.co.uk/api/1.0/jobs/132
    _url = f"{base_url}/jobs/{job_id}"
    return _url

def get_search_url(base_url:Optional[str] = get_base_url()) -> str:
    # https://www.reed.co.uk/api/1.0/search
    JOB_SEARCH_PATH = "search"
    _url = f"{base_url}/{JOB_SEARCH_PATH}"

    return _url

def parse_date_string(date_string: str) -> datetime:
    """
    Parse a date string from the REED API into a datetime object.

    Args:
        date_string (str): The date string from the REED API

    Returns:
        datetime: The parsed datetime object
    """
    return datetime.strptime(date_string, "%d/%m/%Y")


def parse_response(
    response: httpx.Response | Coroutine[Any, Any, httpx.Response],
    parse_func: Callable[[httpx.Response], "_model.APIResponseBaseModel"],
    use_async: bool = False,
) -> "_model.APIResponseBaseModel" | Coroutine[Any, Any, "_model.APIResponseBaseModel"]:
    result: (
        "_model.APIResponseBaseModel"
        | Coroutine[Any, Any, "_model.APIResponseBaseModel"]
    )
    if use_async:
        result = modify_result_async(response, parse_func)

    else:
        if isinstance(response, httpx.Response):
            result = parse_func(response)
        else:
            raise TypeError("response must be a httpx.Response object")

    return result


async def modify_result_async(
    coro, result_parser: Callable[[httpx.Response], Any]
) -> Coroutine[Any, Any, "_model.APIResponseBaseModel"]:

    coro_result: httpx.Response = await coro
    parsed_result = result_parser(coro_result)
    return parsed_result


def _job_search_response_parser(response: httpx.Response) -> "_model.JobSearchResponse":
    print(response)
    print(response.request.url)

    models = [_model.JobSearchPartialJob(**job) for job in response.json()["results"]]
    return _model.JobSearchResponse(
        jobs=models, raw_response=response, raw_request=response.request
    )
