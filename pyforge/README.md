# PyForge CLI

A project scaffolding/build CLI skeleton with structured logging and
[decorlib](https://github.com/Hrishabh-Tomar/decorlib) decorators wired
into every command.

## Install

```bash
pip install -e .
# once decorlib is published, add real dependency:
pip install -e ".[decorlib]"
```

## Subcommands

| Command  | What it does                                  | decorlib decorator(s) used         |
|----------|------------------------------------------------|-------------------------------------|
| `init`   | Scaffold a new project directory                | `@log_calls`, `@validate_types`     |
| `build`  | Run the build step                              | `@log_calls`, `@timeit`             |
| `run`    | Execute the project entrypoint                  | `@log_calls`, `@retry`              |
| `status` | Report project status (cached directory scan)   | `@log_calls`, `@cache`              |
| `clean`  | Remove build artifacts                          | `@log_calls`, `@validate_types`     |

## Logging

Every command logs to `~/.pyforge/pyforge.log` as one JSON object per
line (timestamp, level, logger, message, module, func, line), plus a
plain-text stream to stderr. Override the file with `--log-file`, or
raise console verbosity with `-v/--verbose`.

## Decorlib wiring

`pyforge/decorators.py` imports `retry`, `timeit`, `cache`, `log_calls`,
and `validate_types` from `decorlib` when it's installed. If it isn't
(e.g. running this skeleton standalone before decorlib is on PyPI), it
falls back to small local implementations with the same names and
signatures, so nothing else in the codebase needs to change once you
swap in the real package.

## Project layout

```
pyforge/
├── cli.py              # argparse entrypoint, wires subcommands + logging
├── decorators.py        # decorlib import / fallback shim
├── logging_setup.py     # JSON-line file handler + console handler
└── commands/
    ├── init_cmd.py
    ├── build_cmd.py
    ├── run_cmd.py
    ├── status_cmd.py
    └── clean_cmd.py
```

## Next steps

- Replace the `decorlib` fallback shim with a hard dependency once it's
  published to PyPI.
- Replace the placeholder logic in `build_cmd.py` / `run_cmd.py` with
  real build/run behavior for your project type.
- Add a `tests/` suite (pytest) exercising each subcommand's `run()`.
