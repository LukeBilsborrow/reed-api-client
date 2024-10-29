from typing import Any, Coroutine, Optional
import utils
import httpx

JOB_SEARCH_PATH = "search"


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
        self.session.auth = (self.api_token, "")

    # update the parameters of this function to match the
    def job_search(
        self,
        use_async: bool = False,
        employerId: int = None,
        employerProfileId: int = None,
        keywords: str = None,
        locationName: str = None,
        distanceFromLocation: int = 10,
        permanent: bool = None,
        contract: bool = None,
        temp: bool = None,
        partTime: bool = None,
        fullTime: bool = None,
        minimumSalary: int = None,
        maximumSalary: int = None,
        postedByRecruitmentAgency: bool = None,
        postedByDirectEmployer: bool = None,
        graduate: bool = None,
        resultsToTake: int = 100,
        resultsToSkip: int = 0,
    ):
        # saves the parameters in a dictionary
        # so we don't have to pass them individually
        params = locals()
        del params["self"]

        res = self._make_request(url=f"{self.base_url}/{JOB_SEARCH_PATH}", **params)

        return res

    def _make_request(self, url, use_async=False, **kwargs):
        params = {k: v for k, v in kwargs.items() if v is not None}
        if use_async:
            res: Coroutine[Any, Any, httpx.Response] = self._make_async_request(
                url, params
            )

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
        if not self._async_session:
            self._async_session = httpx.AsyncClient()
