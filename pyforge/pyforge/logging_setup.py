"""
Structured file logging for PyForge.

Emits JSON-lines records to a log file (default: ~/.pyforge/pyforge.log)
plus a human-readable stream to stderr. JSON-lines keeps logs greppable
and easy to ship to something like Datadog/ELK later without changing
the calling code.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOG_DIR = Path.home() / ".pyforge"
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "pyforge.log"


class JsonLineFormatter(logging.Formatter):
    """Renders one JSON object per log record."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging(
    log_file: Path | None = None,
    level: int = logging.INFO,
    verbose: bool = False,
) -> logging.Logger:
    """Configure the root 'pyforge' logger with file + console handlers.

    Call once from cli.py's entrypoint before any subcommand runs.
    """
    log_file = log_file or DEFAULT_LOG_FILE
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("pyforge")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JsonLineFormatter())
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG if verbose else level)
    console_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    logger.addHandler(console_handler)

    logger.propagate = False
    logger.debug("Logging initialized -> %s", log_file)
    return logger
