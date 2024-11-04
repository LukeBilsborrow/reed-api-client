from typing import Any, Coroutine, Literal, Optional, Tuple, overload
import _model
import utils
import httpx


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

    def job_search(
        self,
        use_async: bool = False,
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
    ) -> _model.APIResponseBaseModel | Coroutine[Any, Any, _model.APIResponseBaseModel]:
        # saves the parameters in a dictionary
        # so we don't have to pass them individually
        params = locals()
        del params["self"]

        response_or_coro = self._make_request(
            url=utils.get_search_url(self.base_url), **params
        )

        model = utils.parse_response(
            response_or_coro, utils._job_search_response_parser, use_async=use_async
        )
        return model

    def job_detail(
        self,
        job_id: int,
        use_async: bool = False
    ) -> _model.APIResponseBaseModel | Coroutine[Any, Any, _model.APIResponseBaseModel]:
        #raise NotImplementedError()


        _detail_url = utils.get_detail_url(job_id, self.base_url)
        response_or_coro = self._make_request(url=_detail_url)

        model = utils.parse_response(
            response_or_coro, utils._job_detail_response_parser, use_async=use_async
        )
        return model

    def _make_request(self, url, use_async=False, **kwargs):
        params = {k: v for k, v in kwargs.items() if v is not None}
        if use_async:
            res = self._make_async_request(url, params)

        else:
            res = self._make_sync_request(url, params)

        return res

    def _make_sync_request(self, url, params) -> httpx.Response:
        response = self.session.get(url=url, params=params)
        return response

    def _make_async_request(
        self, url: str, params: dict[str, str]
    ) -> Coroutine[Any, Any, httpx.Response]:
        self._check_async_client()
        coro = self._async_session.get(url=url, params=params)
        return coro

    def _check_async_client(self) -> None:
        if getattr(self, "_async_session", None) is None:
            self._async_session = httpx.AsyncClient()
            self._async_session.auth = (self.api_token, "")  # type: ignore
