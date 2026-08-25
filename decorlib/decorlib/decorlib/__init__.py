"""
decorlib
========

A small collection of dependency-free, well-behaved Python decorators:

    - @retry           retry a call on failure, with backoff/jitter
    - @timeit          measure and report execution time
    - @cache           memoize results, with optional TTL and maxsize
    - @log_calls       log calls, arguments, results, and exceptions
    - @validate_types  validate arguments/return value against type hints

All decorators:
    * work on both plain functions and methods
    * preserve the wrapped function's identity via functools.wraps
    * are usable bare (``@retry``) or parameterized (``@retry(times=5)``)
    * are thread-safe where statefulness is involved (cache)
"""

from .retry import retry
from .timeit import timeit
from .cache import cache, CacheInfo
from .log_calls import log_calls
from .validate_types import validate_types, TypeValidationError

__all__ = [
    "retry",
    "timeit",
    "cache",
    "CacheInfo",
    "log_calls",
    "validate_types",
    "TypeValidationError",
]

__version__ = "0.1.0"
