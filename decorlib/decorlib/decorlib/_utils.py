"""Internal helpers shared across decorlib's decorators."""
import functools
from typing import Any, Callable


def optional_args_decorator(decorator_factory: Callable) -> Callable:
    """
    Allow a decorator factory (a function that returns a decorator) to be
    used both bare and with arguments:

        @retry
        def f(): ...

        @retry(times=5)
        def f(): ...

    ``decorator_factory`` must accept only keyword arguments (besides the
    optional first positional function, which is handled here).
    """

    @functools.wraps(decorator_factory)
    def wrapper(func: Callable = None, **kwargs: Any) -> Callable:
        if func is not None and callable(func):
            # Bare usage: @retry
            return decorator_factory(**kwargs)(func)
        # Parameterized usage: @retry(times=5)
        return decorator_factory(**kwargs)

    return wrapper
