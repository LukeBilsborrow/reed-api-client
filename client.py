from typing import (
    Any,
    Coroutine,
    Optional,
    overload,
)
import _model
import utils
import httpx

from utils import UseSync, UseAsync


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
        sync_type: type[UseSync] = ...,
        employerId: Optional[int] = ...,
        employerProfileId: Optional[int] = ...,
        keywords: Optional[str] = ...,
        locationName: Optional[str] = ...,
        distanceFromLocation: Optional[int] = ...,
        permanent: Optional[bool] = ...,
        contract: Optional[bool] = ...,
        temp: Optional[bool] = ...,
        partTime: Optional[bool] = ...,
        fullTime: Optional[bool] = ...,
        minimumSalary: Optional[int] = ...,
        maximumSalary: Optional[int] = ...,
        postedByRecruitmentAgency: Optional[bool] = ...,
        postedByDirectEmployer: Optional[bool] = ...,
        graduate: Optional[bool] = ...,
        resultsToTake: Optional[int] = ...,
        resultsToSkip: Optional[int] = ...,
    ) -> _model.JobSearchResponse: ...

    @overload
    def job_search(
        self,
        sync_type: type[UseAsync],
        employerId: Optional[int] = ...,
        employerProfileId: Optional[int] = ...,
        keywords: Optional[str] = ...,
        locationName: Optional[str] = ...,
        distanceFromLocation: Optional[int] = ...,
        permanent: Optional[bool] = ...,
        contract: Optional[bool] = ...,
        temp: Optional[bool] = ...,
        partTime: Optional[bool] = ...,
        fullTime: Optional[bool] = ...,
        minimumSalary: Optional[int] = ...,
        maximumSalary: Optional[int] = ...,
        postedByRecruitmentAgency: Optional[bool] = ...,
        postedByDirectEmployer: Optional[bool] = ...,
        graduate: Optional[bool] = ...,
        resultsToTake: Optional[int] = ...,
        resultsToSkip: Optional[int] = ...,
    ) -> Coroutine[Any, Any, _model.JobSearchResponse]: ...

    def job_search(
        self,
        sync_type: type[UseSync] | type[UseAsync] = UseSync,
        employerId: Optional[int] = None,
        employerProfileId: Optional[int] = None,
        keywords: Optional[str] = None,
        locationName: Optional[str] = None,
        distanceFromLocation: Optional[int] = 10,
        permanent: Optional[bool] = None,
        contract: Optional[bool] = None,
        temp: Optional[bool] = None,
        partTime: Optional[bool] = None,
        fullTime: Optional[bool] = None,
        minimumSalary: Optional[int] = None,
        maximumSalary: Optional[int] = None,
        postedByRecruitmentAgency: Optional[bool] = None,
        postedByDirectEmployer: Optional[bool] = None,
        graduate: Optional[bool] = None,
        resultsToTake: Optional[int] = 100,
        resultsToSkip: Optional[int] = 0,
    ) -> _model.JobSearchResponse | Coroutine[Any, Any, _model.JobSearchResponse]:
        # saves the parameters in a dictionary
        # so we don't have to pass them individually
        params = locals()
        del params["self"]
        del params["sync_type"]

        coro_or_response = self._make_request(
            url=utils.get_search_url(self.base_url), sync_type=sync_type, params=params
        )

        return utils.parse_response(
            coro_or_response, utils._job_search_response_parser, sync_type=sync_type
        )

    @overload
    def job_detail(
        self, job_id: int, *, sync_type: type[UseSync] = ...
    ) -> _model.JobDetailResponse: ...

    @overload
    def job_detail(
        self, job_id: int, *, sync_type: type[UseAsync] = ...
    ) -> Coroutine[Any, Any, _model.JobDetailResponse]: ...

    def job_detail(
        self, job_id: int, *, sync_type: type[UseSync] | type[UseAsync] = UseSync
    ):

        detail_url = utils.get_detail_url(job_id, self.base_url)
        response_or_coro = self._make_request(detail_url, sync_type=sync_type)

        model = utils.parse_response(
            response_or_coro, utils._job_detail_response_parser
        )
        return model

    @overload
    def _make_request(
        self, url: str, *, sync_type: type[UseSync] = ..., params: dict[str, Any] = ...
    ) -> httpx.Response: ...

    @overload
    def _make_request(
        self, url: str, *, sync_type: type[UseAsync] = ..., params: dict[str, Any] = ...
    ) -> Coroutine[Any, Any, httpx.Response]: ...

    def _make_request(
        self,
        url: str,
        *,
        sync_type: type[UseSync] | type[UseAsync] = UseSync,
        # probably should not have mutable default
        params: dict[str, Any] = {}
    ) -> httpx.Response | Coroutine[Any, Any, httpx.Response]:
        params = {k: v for k, v in params.items() if v is not None}
        if sync_type is UseAsync:
            _coro: Coroutine[Any, Any, httpx.Response] = self._make_async_request(
                url, params
            )
            return _coro
        else:
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
        self, url: str, params: dict[str, str]
    ) -> Coroutine[Any, Any, httpx.Response]:
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
