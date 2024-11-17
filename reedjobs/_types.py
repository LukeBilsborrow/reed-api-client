from typing import Any, Coroutine, Union

import httpx

PossiblyAsyncResponse = Union[httpx.Response, Coroutine[Any, Any, httpx.Response]]
