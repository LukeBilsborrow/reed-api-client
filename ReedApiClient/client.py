from typing import Any, Coroutine, Mapping, Optional, TypedDict, overload

import httpx

import _model
import utils
from utils import UseAsync, UseSync


class JobSearchParams(TypedDict, total=False):
    employer_id: Optional[int]
    employer_profile_id: Optional[int]
    keywords: Optional[str]
    location_name: Optional[str]
    distance_from_location: Optional[int]
    permanent: Optional[bool]
    contract: Optional[bool]
    temp: Optional[bool]
    part_time: Optional[bool]
    full_time: Optional[bool]
    minimum_salary: Optional[int]
    maximum_salary: Optional[int]
    posted_by_recruitment_agency: Optional[bool]
    posted_by_direct_employer: Optional[bool]
    graduate: Optional[bool]
    results_to_take: Optional[int]
    results_to_skip: Optional[int]


class ReedApiClient:
    # session_Settings: dict
    api_token: str
    _sync_session: httpx.Client
    _async_session: httpx.AsyncClient
    base_url: str

    def __init__(
        self,
        api_token: str,
        override_full_url: Optional[str] = None,
    ):
        self.api_token = api_token
        self.base_url = override_full_url or utils.get_base_url()
        self.session = httpx.Client()
        self.session.auth = (self.api_token, "")  # type: ignore

    @overload
    def job_search(
        self,
        *,
        params: JobSearchParams,
        sync_type: type[UseSync] = ...,
    ) -> _model.JobSearchResponse:
        ...

    @overload
    def job_search(
        self,
        *,
        params: JobSearchParams,
        sync_type: type[UseAsync] = ...,
    ) -> Coroutine[Any, Any, _model.JobSearchResponse]:
        ...

    def job_search(
        self,
        *,
        params: JobSearchParams,
        sync_type: type[UseSync] | type[UseAsync] = UseSync,
    ) -> _model.JobSearchResponse | Coroutine[Any, Any, _model.JobSearchResponse]:

        coro_or_response = self._make_request(utils.get_search_url(self.base_url),
                                              sync_type=sync_type,
                                              params=params)

        return utils.parse_response(coro_or_response, utils.job_search_response_parser)

    @overload
    def job_detail(self,
                   job_id: int,
                   *,
                   sync_type: type[UseSync] = ...) -> _model.JobDetailResponse:
        ...

    @overload
    def job_detail(
            self,
            job_id: int,
            *,
            sync_type: type[UseAsync] = ...) -> Coroutine[Any, Any, _model.JobDetailResponse]:
        ...

    def job_detail(self, job_id: int, *, sync_type: type[UseSync] | type[UseAsync] = UseSync):

        detail_url = utils.get_detail_url(job_id, self.base_url)
        response_or_coro = self._make_request(detail_url, sync_type=sync_type)

        model = utils.parse_response(response_or_coro, utils.job_detail_response_parser)
        return model

    @overload
    def _make_request(self,
                      url: str,
                      *,
                      sync_type: type[UseSync] = ...,
                      params: Optional[Mapping[str, Any]] = ...) -> httpx.Response:
        ...

    @overload
    def _make_request(
            self,
            url: str,
            *,
            sync_type: type[UseAsync] = ...,
            params: Optional[Mapping[str, Any]] = ...) -> Coroutine[Any, Any, httpx.Response]:
        ...

    def _make_request(
        self,
        url: str,
        *,
        sync_type: type[UseSync] | type[UseAsync] = UseSync,
        # probably should not have mutable default
        params: Optional[Mapping[str, Any]] = None
    ) -> httpx.Response | Coroutine[Any, Any, httpx.Response]:
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        if sync_type is UseAsync:
            _coro: Coroutine[Any, Any, httpx.Response] = self._make_async_request(url, params)
            return _coro

        # TODO add error handling
        response = self._make_sync_request(url, params)
        return response

    def _make_sync_request(self, url, params) -> httpx.Response:
        # if the request fails, we want to attempt to provide a more useful error
        try:
            response = self.session.get(url=url, params=params)

        # TODO catch more specific exceptions
        except BaseException as e:
            # TODO add logging
            raise e
        response = utils.check_response(response)

        return response

    def _make_async_request(
            self, url: str, params: Optional[Mapping[str,
                                                     Any]]) -> Coroutine[Any, Any, httpx.Response]:
        self._check_async_client()
        coro = self._async_session.get(url=url, params=params)

        async def _check_response_wrapper(response_coro):
            try:
                response = await response_coro
            # TODO catch more specific exceptions
            except BaseException as e:
                # TODO add logging
                raise e
            response = utils.check_response(response)

            return response

        coro = _check_response_wrapper(coro)
        return coro

    def _check_async_client(self) -> None:
        if getattr(self, "_async_session", None) is None:
            self._async_session = httpx.AsyncClient()
            self._async_session.auth = (self.api_token, "")  # type: ignore
