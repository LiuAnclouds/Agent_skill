# Module Guide: `experiment/eda/run_eda.py`

## Purpose

CLI entrypoint for the EDA pipeline.

## When To Read This File

Read this file when you need the exact EDA CLI surface or want to add a new user-facing EDA command-line option.

## Upstream Callers / Entrypoints

- shell / terminal

## Downstream Consumers / Artifacts

- experiment/eda/analysis.py

## Main Outputs Or Side Effects

- EDA run entrypoint only; artifacts are written by analysis.py

## Common Edit Hotspots

- Expose new analysis stages or flags here after analysis.py changes.

## Top-Level Symbols

### `parse_args() -> argparse.Namespace`

- Kind: `function`
- Lines: `15-38`
- Role: Parse CLI flags for phase selection, analysis modules, and output directory.
- How to use: Called automatically by `main()` to define the user-facing CLI contract.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `main() -> None`

- Kind: `function`
- Lines: `41-46`
- Role: Entrypoint that expands phase selection and launches run_eda().
- How to use: Run this through the file's CLI command; `main()` is the terminal-facing orchestration entrypoint.
- Side effects / outputs: Produces the file's main side effects or terminal outputs.

