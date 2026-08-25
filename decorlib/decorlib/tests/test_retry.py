import pytest
from decorlib import retry
from decorlib.retry import RetryError


def test_retry_succeeds_after_failures():
    calls = {"n": 0}

    @retry(times=3, delay=0)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("not yet")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3


def test_retry_bare_usage():
    calls = {"n": 0}

    @retry
    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("nope")
        return "ok"

    assert flaky() == "ok"


def test_retry_exhausts_and_reraises():
    @retry(times=2, delay=0)
    def always_fails():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        always_fails()


def test_retry_no_reraise_wraps_in_retry_error():
    @retry(times=2, delay=0, reraise=False)
    def always_fails():
        raise ValueError("boom")

    with pytest.raises(RetryError) as exc_info:
        always_fails()
    assert exc_info.value.attempts == 2


def test_retry_only_catches_specified_exceptions():
    @retry(times=2, delay=0, exceptions=KeyError)
    def raises_value_error():
        raise ValueError("not a KeyError")

    with pytest.raises(ValueError):
        raises_value_error()


def test_retry_on_retry_hook_called():
    seen = []

    @retry(times=3, delay=0, on_retry=lambda attempt, exc: seen.append(attempt))
    def flaky():
        if len(seen) < 2:
            raise ValueError("retry me")
        return "done"

    assert flaky() == "done"
    assert seen == [1, 2]
