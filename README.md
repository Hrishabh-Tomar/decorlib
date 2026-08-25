# decorlib

A small, dependency-free collection of production-minded Python decorators — built to be dropped into any project with zero extra setup.

| Decorator | What it does |
|---|---|
| `@retry` | Automatically retries a function if it raises an exception, with configurable delay, exponential backoff, and jitter |
| `@timeit` | Measures and reports how long a function takes to run |
| `@cache` | Memoizes results (like `functools.lru_cache`, plus optional TTL expiry and thread safety) |
| `@log_calls` | Logs every call — arguments, return value, and any exception raised |
| `@validate_types` | Validates a function's arguments and return value against its type hints at runtime |

Requires **Python 3.8+**. No third-party dependencies.

---

## Why this exists

Type hints in Python don't actually get enforced. Retry logic, timing, caching, and call logging are things almost every real project needs eventually — and they usually get rewritten from scratch, copy-pasted between repos, or bolted on ad-hoc. `decorlib` packages five of the most common ones properly: tested, documented, and installable like any other library.

---

## Install

**From a wheel:**
```bash
pip install decorlib-0.1.0-py3-none-any.whl
```

**From source (editable, for development):**
```bash
git clone https://github.com/Hrishabh-Tomar/decorlib.git
cd decorlib
pip install -e .
```

---

## Usage

Every decorator works **bare** (`@retry`) or **configured** (`@retry(times=5)`) — no special syntax to remember.

### `@retry`

Retries a function on failure, with optional delay, backoff multiplier, and jitter.

```python
from decorlib import retry

@retry(times=5, exceptions=ConnectionError, delay=0.5, backoff=2, jitter=0.1)
def fetch(url):
    ...
```

| Param | Default | Meaning |
|---|---|---|
| `times` | 3 | Max attempts |
| `exceptions` | `Exception` | Exception type(s) to catch and retry on |
| `delay` | 0 | Initial delay (seconds) before retrying |
| `backoff` | 1 | Multiplier applied to delay after each attempt |
| `jitter` | 0 | Extra random seconds added to each delay |
| `reraise` | `True` | Re-raise the last exception, or raise `RetryError` wrapping it |
| `on_retry` | `None` | Optional `callback(attempt, exception)` before each retry |

### `@timeit`

Measures execution time and reports it.

```python
from decorlib import timeit

@timeit(unit="ms", precision=2)
def compute():
    ...

compute()
print(compute.last_duration)  # duration of the most recent call
```

| Param | Default | Meaning |
|---|---|---|
| `unit` | `"s"` | `"s"`, `"ms"`, or `"us"` |
| `precision` | 4 | Decimal places in the printed report |
| `logger` | `print` | Callable that receives the report string |
| `on_time` | `None` | Optional `callback(func_name, elapsed)` instead of printing |

### `@cache`

Memoizes results with LRU eviction and optional expiry.

```python
from decorlib import cache

@cache(maxsize=256, ttl=60)
def expensive(x):
    ...

expensive.cache_info()   # CacheInfo(hits=.., misses=.., maxsize=.., currsize=..)
expensive.cache_clear()
```

| Param | Default | Meaning |
|---|---|---|
| `maxsize` | 128 | LRU eviction cap, or `None` for unbounded |
| `ttl` | `None` | Seconds before an entry expires, or `None` to never expire |
| `typed` | `False` | If `True`, arguments of different types are cached separately |

Thread-safe.

### `@log_calls`

Logs every call, its arguments, its result, and any exception.

```python
import logging
from decorlib import log_calls

@log_calls(logger=logging.getLogger("myapp"), level=logging.DEBUG)
def process(order_id, retry=False):
    ...
```

| Param | Default | Meaning |
|---|---|---|
| `logger` | `decorlib.log_calls` logger | A `logging.Logger` to write to |
| `level` | `logging.INFO` | Log level for all emitted records |
| `log_args` | `True` | Include arguments in the log |
| `log_result` | `True` | Log the return value |
| `log_exceptions` | `True` | Log exceptions before they propagate |

### `@validate_types`

Validates arguments and return value against the function's own type hints.

```python
from typing import List, Optional, Union
from decorlib import validate_types

@validate_types
def total(values: List[int], discount: Optional[float] = None) -> Union[int, float]:
    ...
```

Supports plain types, `Optional`, `Union`, and parameterized `List` / `Dict` / `Tuple` / `Set`. Raises `decorlib.TypeValidationError` (a `TypeError` subclass) on mismatch.

Pass `check_return=False` to skip validating the return value.

---

## Stacking decorators

All decorators use `functools.wraps`, so they compose cleanly in any order:

```python
from decorlib import retry, timeit, cache, log_calls, validate_types

@log_calls
@timeit
@retry(times=3)
@cache(ttl=30)
@validate_types
def get_user(user_id: int) -> dict:
    ...
```

---

## Limitations

- Targets **synchronous** functions only — `async def` is not currently supported.
- `@validate_types` does a best-effort structural check. Deeply nested or exotic typing constructs (`Protocol`, `TypedDict`, custom generics) are skipped rather than raising a false positive.

---

## Development

```bash
pip install -e .
pip install pytest
pytest
```

24 tests, all passing.

**Build a distributable package:**
```bash
python -m pip install build
python -m build
# -> dist/decorlib-0.1.0-py3-none-any.whl
#    dist/decorlib-0.1.0.tar.gz
```

---

## License

MIT
