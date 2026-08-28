from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from pyforge.decorators import log_calls, validate_types

BUILD_ARTIFACT_DIRS = ("build", "dist", "__pycache__", ".pyforge-cache")


@log_calls
@validate_types
def run(args: argparse.Namespace) -> int:
    """Remove build artifacts under the project root."""
    root = Path(args.path).expanduser().resolve()
    removed = 0
    for dirname in BUILD_ARTIFACT_DIRS:
        for match in root.rglob(dirname):
            if match.is_dir():
                if args.dry_run:
                    print(f"[dry-run] would remove {match}")
                else:
                    shutil.rmtree(match, ignore_errors=True)
                    print(f"removed {match}")
                removed += 1
    print(f"{'Would clean' if args.dry_run else 'Cleaned'} {removed} artifact dir(s).")
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("clean", help="Remove build artifacts")
    parser.add_argument("path", nargs="?", default=".", help="Project directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed")
    parser.set_defaults(handler=run)
