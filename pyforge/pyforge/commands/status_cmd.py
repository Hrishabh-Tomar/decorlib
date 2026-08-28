from __future__ import annotations

import argparse
import re
from pathlib import Path

from pyforge.decorators import cache, log_calls

# Directories we never want to count as "project" files: virtualenvs,
# caches, and VCS metadata. Matched by directory name anywhere in the tree.
# Regexes so variants like .venv1, venv-311, env_backup all get caught,
# not just the exact names ".venv" / "venv" / "env".
EXCLUDED_DIR_REGEXES = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"^\.?venv.*$",        # venv, .venv, venv1, .venv1, venv-311, venvs ...
        r"^\.?virtualenv.*$",
        r"^env\d*$",
        r"^__pycache__$",
        r"^\.git$",
        r"^\.mypy_cache$",
        r"^\.pytest_cache$",
        r"^node_modules$",
        r"^build$",
        r"^dist$",
        r".*\.egg-info$",
    )
)


def _is_excluded(path: Path) -> bool:
    return any(regex.match(part) for part in path.parts for regex in EXCLUDED_DIR_REGEXES)


@cache
def _scan_project(root: str) -> dict:
    """Expensive-ish directory scan; cached so repeat `status` calls in
    the same process (e.g. a long-running shell) are cheap. Skips
    virtualenvs, caches, and VCS dirs so counts reflect real source."""
    root_path = Path(root)
    files = [
        f for f in (root_path.rglob("*.py") if root_path.exists() else [])
        if not _is_excluded(f.relative_to(root_path))
    ]
    return {"root": root, "python_files": len(files)}


@log_calls
def run(args: argparse.Namespace) -> int:
    """Report basic project status."""
    info = _scan_project(args.path)
    print(f"Project root: {info['root']}")
    print(f"Python files: {info['python_files']}")
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("status", help="Show project status")
    parser.add_argument("path", nargs="?", default=".", help="Project directory")
    parser.set_defaults(handler=run)
