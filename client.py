from typing import Optional
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

        
    def _make_sync_request(self, url, json):
        response = self.session.post(url=url, json=json)
        return self._to_api_result(response)
    
    def _make_async_request(self, url, json):
        response = self.session.post(url=url, json=json)

    def _check_async_client(self) -> None:
        if not self._async_session:
            self._async_session = httpx.AsyncClient()

        