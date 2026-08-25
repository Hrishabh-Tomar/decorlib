"""@retry — retry a callable on failure, with backoff, jitter, and hooks."""
import functools
import random
import time
from typing import Any, Callable, Tuple, Type, Union

from ._utils import optional_args_decorator

ExceptionSpec = Union[Type[BaseException], Tuple[Type[BaseException], ...]]


class RetryError(Exception):
    """Raised when all retry attempts are exhausted (only if reraise=False)."""

    def __init__(self, func_name: str, attempts: int, last_exception: BaseException):
        self.func_name = func_name
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(
            f"{func_name!r} failed after {attempts} attempt(s); "
            f"last error: {last_exception!r}"
        )


def _retry_impl(
    *,
    times: int = 3,
    exceptions: ExceptionSpec = Exception,
    delay: float = 0.0,
    backoff: float = 1.0,
    jitter: float = 0.0,
    reraise: bool = True,
    on_retry: Callable[[int, BaseException], None] = None,
) -> Callable:
    if times < 1:
        raise ValueError("times must be >= 1")
    if backoff < 1:
        raise ValueError("backoff must be >= 1")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception: BaseException = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt == times:
                        break
                    if on_retry is not None:
                        on_retry(attempt, exc)
                    if current_delay > 0 or jitter > 0:
                        sleep_for = current_delay + (
                            random.uniform(0, jitter) if jitter else 0
                        )
                        time.sleep(sleep_for)
                    current_delay *= backoff
            if reraise:
                raise last_exception
            raise RetryError(func.__name__, times, last_exception)

        wrapper.__wrapped__ = func
        return wrapper

    return decorator


retry = optional_args_decorator(_retry_impl)
