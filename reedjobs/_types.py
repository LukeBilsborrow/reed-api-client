from __future__ import annotations

from typing import Any, Coroutine, NewType, Type, Union

import httpx

UseSync = NewType("UseSync", bool)
UseAsync = NewType("UseAsync", bool)

PossiblyAsyncResponse = Union[httpx.Response, Coroutine[Any, Any, httpx.Response]]
Syncness = Union[Type[UseSync], Type[UseAsync]]
