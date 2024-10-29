from typing import Any, Coroutine, Optional
import utils
import httpx
class ReedApiClient:
    #session_Settings: dict
    api_token: str
    _sync_session: httpx.Client
    _async_session: httpx.AsyncClient
    base_url: str 
    def __init__(
        self,
        api_token: str,
        use_https: bool = False,
        override_full_url: Optional[str] = None,
    ):
        self.api_token = api_token
        self.base_url = override_full_url if override_full_url else utils.get_base_url(protocol="https" if use_https else "http")
        self.session = httpx.Client()

    def _make_request(self, url, json, use_async=False):
        if use_async:
            res: Coroutine[Any, Any, httpx.Response] = self._make_async_request(url, json)

        else:
            res = self._make_sync_request(url, json)

        return res
        
    def _make_sync_request(self, url, json) -> httpx.Response:
        response = self.session.post(url=url, json=json)
        return self._to_api_result(response)
    
    def _make_async_request(self, url: str, params: dict[str, str]) -> Coroutine[Any, Any, httpx.Response]:
        self._check_async_client()
        
        return self._async_session.get(url=url, params=params)

    def _check_async_client(self) -> None:
        if not self._async_session:
            self._async_session = httpx.AsyncClient()

        