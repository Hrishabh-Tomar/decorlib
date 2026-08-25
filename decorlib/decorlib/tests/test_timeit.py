import time
from decorlib import timeit


def test_timeit_bare_usage_records_duration():
    @timeit
    def fast():
        return 42

    assert fast() == 42
    assert fast.last_duration is not None
    assert fast.last_duration >= 0


def test_timeit_on_time_callback():
    captured = {}

    @timeit(on_time=lambda name, elapsed: captured.update(name=name, elapsed=elapsed))
    def slow():
        time.sleep(0.01)
        return "done"

    assert slow() == "done"
    assert captured["name"] == "slow"
    assert captured["elapsed"] >= 0.01


def test_timeit_records_duration_even_on_exception():
    @timeit
    def boom():
        raise RuntimeError("bad")

    try:
        boom()
    except RuntimeError:
        pass
    assert boom.last_duration is not None
