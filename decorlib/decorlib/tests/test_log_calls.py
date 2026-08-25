import logging
import pytest
from decorlib import log_calls


def test_log_calls_bare_usage(caplog):
    @log_calls
    def add(a, b):
        return a + b

    with caplog.at_level(logging.INFO, logger="decorlib.log_calls"):
        assert add(2, 3) == 5

    messages = [r.message for r in caplog.records]
    assert any("CALL" in m and "add(2, 3)" in m for m in messages)
    assert any("RETURN" in m and "5" in m for m in messages)


def test_log_calls_logs_exceptions(caplog):
    @log_calls
    def boom():
        raise ValueError("bad")

    with caplog.at_level(logging.INFO, logger="decorlib.log_calls"):
        with pytest.raises(ValueError):
            boom()

    messages = [r.message for r in caplog.records]
    assert any("RAISE" in m and "ValueError" in m for m in messages)


def test_log_calls_custom_logger():
    custom_logger = logging.getLogger("myapp.custom")
    records = []
    handler = logging.Handler()
    handler.emit = lambda record: records.append(record)
    custom_logger.addHandler(handler)
    custom_logger.setLevel(logging.INFO)

    @log_calls(logger=custom_logger)
    def f():
        return 1

    f()
    assert any("CALL" in r.getMessage() and "f()" in r.getMessage() for r in records)
