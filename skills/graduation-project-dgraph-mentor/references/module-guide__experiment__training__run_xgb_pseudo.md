# Module Guide: `experiment/training/run_xgb_pseudo.py`

## Purpose

Project module inside experiment/.

## When To Read This File

Read this file when its module role matches the current task.

## Upstream Callers / Entrypoints

- No specific upstream note recorded.

## Downstream Consumers / Artifacts

- No specific downstream note recorded.

## Main Outputs Or Side Effects

- See the symbol list below.

## Common Edit Hotspots

- No custom change hotspot note recorded.

## Top-Level Symbols

### `parse_args() -> argparse.Namespace`

- Kind: `function`
- Lines: `27-78`
- Role: CLI argument parser for this module.
- How to use: Called automatically by `main()` to define the user-facing CLI contract.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_load_prediction_bundle(path: Path) -> dict[str, np.ndarray]`

- Kind: `function`
- Lines: `81-87`
- Role: Load helper that restores data, configuration, or saved artifacts from disk.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `_prediction_path(run_dir: Path, split_name: str) -> Path`

- Kind: `function`
- Lines: `90-97`
- Role: Inference helper that converts a fitted model into fraud probabilities or scores.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_select_pseudo_indices(probabilities: np.ndarray, pos_threshold: float, neg_threshold: float, neg_ratio_cap: float, max_nodes: int | None) -> tuple[np.ndarray, np.ndarray]`

- Kind: `function`
- Lines: `100-133`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `main() -> None`

- Kind: `function`
- Lines: `136-283`
- Role: Module entrypoint that orchestrates the main workflow.
- How to use: Run this through the file's CLI command; `main()` is the terminal-facing orchestration entrypoint.
- Side effects / outputs: Produces the file's main side effects or terminal outputs.

