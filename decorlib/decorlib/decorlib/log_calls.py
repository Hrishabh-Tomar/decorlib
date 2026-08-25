"""@log_calls — log a function's calls, arguments, results, and exceptions."""
import functools
import logging
from typing import Any, Callable

from ._utils import optional_args_decorator

_default_logger = logging.getLogger("decorlib.log_calls")


def _format_call(func_name: str, args: tuple, kwargs: dict) -> str:
    parts = [repr(a) for a in args]
    parts += [f"{k}={v!r}" for k, v in kwargs.items()]
    return f"{func_name}({', '.join(parts)})"


def _log_calls_impl(
    *,
    logger: logging.Logger = None,
    level: int = logging.INFO,
    log_args: bool = True,
    log_result: bool = True,
    log_exceptions: bool = True,
) -> Callable:
    log = logger or _default_logger

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            call_repr = (
                _format_call(func.__qualname__, args, kwargs)
                if log_args
                else f"{func.__qualname__}(...)"
            )
            log.log(level, "CALL %s", call_repr)
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                if log_exceptions:
                    log.log(
                        level,
                        "RAISE %s -> %s: %s",
                        call_repr,
                        type(exc).__name__,
                        exc,
                    )
                raise
            if log_result:
                log.log(level, "RETURN %s -> %r", call_repr, result)
            return result

        wrapper.__wrapped__ = func
        return wrapper

    return decorator


log_calls = optional_args_decorator(_log_calls_impl)
