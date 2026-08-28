"""
Wires PyForge into decorlib (https://github.com/Hrishabh-Tomar/decorlib).

If decorlib is installed (``pip install decorlib``), we use it directly.
Otherwise we fall back to small local implementations with the same
names/signatures so the CLI skeleton still runs standalone. Swap the
fallback block out once decorlib is a hard dependency in pyproject.toml.
"""
from __future__ import annotations

import functools
import time
from typing import Any, Callable

try:
    from decorlib import retry, timeit, cache, log_calls, validate_types  # type: ignore
    USING_DECORLIB = True
except ImportError:
    USING_DECORLIB = False

    def retry(times: int = 3, delay: float = 0.5, exceptions: tuple = (Exception,)):
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exc = None
                for attempt in range(1, times + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as exc:  # noqa: PERF203
                        last_exc = exc
                        if attempt < times:
                            time.sleep(delay)
                raise last_exc
            return wrapper
        return decorator

    def timeit(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger = kwargs.get("_logger") or _module_logger()
                logger.debug("%s took %.2fms", func.__qualname__, elapsed_ms)
        return wrapper

    def cache(func: Callable) -> Callable:
        store: dict = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key not in store:
                store[key] = func(*args, **kwargs)
            return store[key]
        wrapper.cache_clear = store.clear  # type: ignore[attr-defined]
        return wrapper

    def log_calls(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = _module_logger()
            logger.info("CALL %s(args=%s, kwargs=%s)", func.__qualname__, args, kwargs)
            result = func(*args, **kwargs)
            logger.info("RETURN %s -> %r", func.__qualname__, result)
            return result
        return wrapper

    def validate_types(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import typing
            try:
                hints = typing.get_type_hints(func)
            except Exception:
                hints = {}
            bound = _bind_args(func, args, kwargs)
            for name, value in bound.items():
                expected = hints.get(name)
                if (
                    expected
                    and expected is not Any
                    and isinstance(expected, type)
                    and not isinstance(value, expected)
                ):
                    raise TypeError(
                        f"{func.__qualname__}: argument '{name}' expected "
                        f"{expected}, got {type(value).__name__}"
                    )
            return func(*args, **kwargs)
        return wrapper

    def _bind_args(func: Callable, args: tuple, kwargs: dict) -> dict:
        import inspect
        sig = inspect.signature(func)
        try:
            bound = sig.bind_partial(*args, **kwargs)
            return dict(bound.arguments)
        except TypeError:
            return {}

    def _module_logger():
        import logging
        return logging.getLogger("pyforge")

__all__ = ["retry", "timeit", "cache", "log_calls", "validate_types", "USING_DECORLIB"]
