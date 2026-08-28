from __future__ import annotations

import argparse
from pathlib import Path

from pyforge.decorators import log_calls, validate_types


@log_calls
@validate_types
def run(args: argparse.Namespace) -> int:
    """Scaffold a new project directory with a minimal layout."""
    target: Path = Path(args.path).expanduser().resolve()
    if target.exists() and any(target.iterdir()) and not args.force:
        print(f"error: {target} already exists and is not empty (use --force)")
        return 1

    (target / "src").mkdir(parents=True, exist_ok=True)
    (target / "tests").mkdir(parents=True, exist_ok=True)
    (target / "README.md").write_text(f"# {target.name}\n")

    print(f"Initialized project at {target}")
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("init", help="Scaffold a new project directory")
    parser.add_argument("path", nargs="?", default=".", help="Directory to initialize")
    parser.add_argument("--force", action="store_true", help="Init even if directory is non-empty")
    parser.set_defaults(handler=run)
