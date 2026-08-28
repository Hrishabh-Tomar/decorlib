from __future__ import annotations

import argparse
import subprocess

from pyforge.decorators import log_calls, retry


@log_calls
@retry(times=3, delay=0.5, exceptions=(subprocess.SubprocessError,))
def run(args: argparse.Namespace) -> int:
    """Run the project's entrypoint, retrying on transient subprocess errors."""
    print(f"Running '{args.entrypoint}'...")
    result = subprocess.run(args.entrypoint, shell=True)
    return result.returncode


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("run", help="Run the project entrypoint")
    parser.add_argument("entrypoint", help="Command to execute")
    parser.set_defaults(handler=run)
