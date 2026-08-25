"""@cache — memoize a function's results, with optional TTL and maxsize."""
import functools
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, NamedTuple, Optional

from ._utils import optional_args_decorator


class CacheInfo(NamedTuple):
    hits: int
    misses: int
    maxsize: Optional[int]
    currsize: int


def _make_key(args: tuple, kwargs: dict) -> tuple:
    key = args
    if kwargs:
        key += (object(),)  # separator so f(1, x=2) != f(1, 2)
        key += tuple(sorted(kwargs.items()))
    return key


def _cache_impl(
    *,
    maxsize: Optional[int] = 128,
    ttl: Optional[float] = None,
    typed: bool = False,
) -> Callable:
    if maxsize is not None and maxsize < 0:
        raise ValueError("maxsize must be >= 0 or None")
    if ttl is not None and ttl <= 0:
        raise ValueError("ttl must be > 0")

    def decorator(func: Callable) -> Callable:
        store: "OrderedDict[tuple, Any]" = OrderedDict()
        timestamps: dict = {}
        lock = threading.RLock()
        hits = 0
        misses = 0

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal hits, misses
            key = _make_key(args, kwargs)
            if typed:
                key += tuple(type(a) for a in args)
                key += tuple(type(v) for v in kwargs.values())

            with lock:
                if key in store:
                    if ttl is not None and (time.monotonic() - timestamps[key]) > ttl:
                        del store[key]
                        del timestamps[key]
                    else:
                        store.move_to_end(key)
                        hits += 1
                        return store[key]
                misses += 1

            result = func(*args, **kwargs)

            with lock:
                store[key] = result
                timestamps[key] = time.monotonic()
                store.move_to_end(key)
                if maxsize is not None:
                    while len(store) > maxsize:
                        oldest_key, _ = store.popitem(last=False)
                        timestamps.pop(oldest_key, None)
            return result

        def cache_clear() -> None:
            with lock:
                store.clear()
                timestamps.clear()
                nonlocal hits, misses
                hits = 0
                misses = 0

        def cache_info() -> CacheInfo:
            with lock:
                return CacheInfo(hits, misses, maxsize, len(store))

        wrapper.cache_clear = cache_clear
        wrapper.cache_info = cache_info
        wrapper.__wrapped__ = func
        return wrapper

    return decorator


cache = optional_args_decorator(_cache_impl)
