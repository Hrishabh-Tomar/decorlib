from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from pyforge.commands import build_cmd, clean_cmd, init_cmd, run_cmd, status_cmd
from pyforge.logging_setup import DEFAULT_LOG_FILE, setup_logging

SUBCOMMANDS = (init_cmd, build_cmd, run_cmd, status_cmd, clean_cmd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyforge",
        description="PyForge - project scaffolding and build CLI",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_LOG_FILE,
        help=f"Path to the structured log file (default: {DEFAULT_LOG_FILE})",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose console output")

    subparsers = parser.add_subparsers(dest="command", required=True)
    for module in SUBCOMMANDS:
        module.register(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logger = setup_logging(log_file=args.log_file, verbose=args.verbose)

    try:
        return args.handler(args)
    except Exception:
        logger.exception("Unhandled error in command '%s'", args.command)
        print(f"error: command '{args.command}' failed — see {args.log_file}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
