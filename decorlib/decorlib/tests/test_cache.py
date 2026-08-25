import time
from decorlib import cache


def test_cache_bare_usage_deduplicates_calls():
    calls = {"n": 0}

    @cache
    def add(a, b):
        calls["n"] += 1
        return a + b

    assert add(1, 2) == 3
    assert add(1, 2) == 3
    assert calls["n"] == 1
    info = add.cache_info()
    assert info.hits == 1
    assert info.misses == 1


def test_cache_maxsize_evicts_lru():
    @cache(maxsize=2)
    def square(x):
        return x * x

    square(1)
    square(2)
    square(3)  # evicts 1
    info = square.cache_info()
    assert info.currsize == 2


def test_cache_ttl_expires_entries():
    calls = {"n": 0}

    @cache(ttl=0.05)
    def now(_marker):
        calls["n"] += 1
        return calls["n"]

    first = now("x")
    time.sleep(0.08)
    second = now("x")
    assert first != second


def test_cache_clear_resets_state():
    @cache
    def identity(x):
        return x

    identity(1)
    identity.cache_clear()
    info = identity.cache_info()
    assert info.currsize == 0
    assert info.hits == 0
    assert info.misses == 0


def test_cache_distinguishes_positional_and_keyword():
    calls = {"n": 0}

    @cache
    def f(a, b=2):
        calls["n"] += 1
        return a + b

    f(1, 2)
    f(1, b=2)
    assert calls["n"] == 2
