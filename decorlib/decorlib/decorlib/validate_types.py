"""@validate_types — validate a call's arguments/return value against annotations."""
import functools
import inspect
import typing
from typing import Any, Callable, Union

from ._utils import optional_args_decorator


class TypeValidationError(TypeError):
    """Raised when an argument or return value doesn't match its annotation."""


def _check(value: Any, expected: Any, label: str) -> None:
    if expected is Any or expected is inspect.Signature.empty:
        return

    origin = typing.get_origin(expected)

    if origin is Union:
        args = typing.get_args(expected)
        for arg in args:
            try:
                _check(value, arg, label)
                return
            except TypeValidationError:
                continue
        names = " | ".join(getattr(a, "__name__", str(a)) for a in args)
        raise TypeValidationError(
            f"{label} must be one of ({names}), got {type(value).__name__}"
        )

    if origin is not None:
        # Parameterized generic, e.g. List[int], Dict[str, int], Tuple[int, ...]
        if not isinstance(value, origin):
            raise TypeValidationError(
                f"{label} must be {origin.__name__}, got {type(value).__name__}"
            )
        args = typing.get_args(expected)
        if not args:
            return
        if origin in (list, set, frozenset) and isinstance(value, (list, set, frozenset)):
            (item_type,) = args
            for i, item in enumerate(value):
                _check(item, item_type, f"{label}[{i}]")
        elif origin is dict and isinstance(value, dict):
            key_type, val_type = args
            for k, v in value.items():
                _check(k, key_type, f"{label} key {k!r}")
                _check(v, val_type, f"{label}[{k!r}]")
        elif origin is tuple and isinstance(value, tuple):
            if len(args) == 2 and args[1] is Ellipsis:
                for i, item in enumerate(value):
                    _check(item, args[0], f"{label}[{i}]")
            elif len(args) == len(value):
                for i, (item, t) in enumerate(zip(value, args)):
                    _check(item, t, f"{label}[{i}]")
        return

    if not isinstance(expected, type):
        return  # unsupported/unknown annotation form; skip rather than false-positive

    if not isinstance(value, expected):
        raise TypeValidationError(
            f"{label} must be {expected.__name__}, got {type(value).__name__}"
        )


def _validate_types_impl(*, check_return: bool = True) -> Callable:
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)
        try:
            hints = typing.get_type_hints(func)
        except Exception:
            hints = getattr(func, "__annotations__", {})

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for name, value in bound.arguments.items():
                if name in hints:
                    _check(value, hints[name], f"Argument {name!r} of {func.__qualname__}")

            result = func(*args, **kwargs)

            if check_return and "return" in hints:
                _check(result, hints["return"], f"Return value of {func.__qualname__}")
            return result

        wrapper.__wrapped__ = func
        return wrapper

    return decorator


validate_types = optional_args_decorator(_validate_types_impl)
