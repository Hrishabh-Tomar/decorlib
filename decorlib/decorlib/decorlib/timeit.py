"""@timeit — measure and report a function's execution time."""
import functools
import time
from typing import Any, Callable

from ._utils import optional_args_decorator


def _timeit_impl(
    *,
    precision: int = 4,
    logger: Callable[[str], None] = None,
    unit: str = "s",
    on_time: Callable[[str, float], None] = None,
) -> Callable:
    if unit not in ("s", "ms", "us"):
        raise ValueError("unit must be one of 's', 'ms', 'us'")
    multiplier = {"s": 1, "ms": 1_000, "us": 1_000_000}[unit]
    emit = logger or print

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = (time.perf_counter() - start) * multiplier
                wrapper.last_duration = elapsed
                if on_time is not None:
                    on_time(func.__name__, elapsed)
                else:
                    emit(f"{func.__qualname__} took {elapsed:.{precision}f}{unit}")

        wrapper.last_duration = None
        wrapper.__wrapped__ = func
        return wrapper

    return decorator


timeit = optional_args_decorator(_timeit_impl)
