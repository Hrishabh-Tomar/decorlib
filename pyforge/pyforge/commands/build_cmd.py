from __future__ import annotations

import argparse
import time

from pyforge.decorators import log_calls, timeit


@log_calls
@timeit
def run(args: argparse.Namespace) -> int:
    """Simulate a build step (placeholder for real build logic)."""
    print(f"Building target '{args.target}' ({'release' if args.release else 'debug'})...")
    time.sleep(0.2)  # placeholder for real build work
    print("Build complete.")
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("build", help="Build the project")
    parser.add_argument("target", nargs="?", default="all", help="Build target")
    parser.add_argument("--release", action="store_true", help="Build in release mode")
    parser.set_defaults(handler=run)
