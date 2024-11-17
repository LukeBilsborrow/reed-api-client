from typing import Any, Coroutine, NewType, Union

import httpx

UseSync = NewType("UseSync", bool)
UseAsync = NewType("UseAsync", bool)

PossiblyAsyncResponse = Union[httpx.Response, Coroutine[Any, Any, httpx.Response]]
Syncness = Union[type[UseSync], type[UseAsync]]
