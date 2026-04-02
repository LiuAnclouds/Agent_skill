# Module Guide: `experiment/training/run_xgb_multiclass_bg_graphprop.py`

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
- Lines: `32-119`
- Role: CLI argument parser for this module.
- How to use: Called automatically by `main()` to define the user-facing CLI contract.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_cache_key(args: argparse.Namespace, threshold_day: int) -> str`

- Kind: `function`
- Lines: `122-139`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_multiclass_binary_auc(predt: np.ndarray, dmatrix) -> tuple[str, float]`

- Kind: `function`
- Lines: `142-149`
- Role: Metric helper used to evaluate fraud-detection predictions.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_binary_score_from_softprob(prob: np.ndarray) -> np.ndarray`

- Kind: `function`
- Lines: `152-154`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_build_sample_weight(y_train: np.ndarray, args: argparse.Namespace, train_first_active: np.ndarray | None = None, threshold_day: int | None = None) -> dict[str, float | dict[str, float]]`

- Kind: `function`
- Lines: `157-202`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `_write_feature_importance(booster, feature_names: list[str], path: Path) -> None`

- Kind: `function`
- Lines: `205-215`
- Role: Artifact-writing helper used to persist outputs for later reuse.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `main() -> None`

- Kind: `function`
- Lines: `218-369`
- Role: Module entrypoint that orchestrates the main workflow.
- How to use: Run this through the file's CLI command; `main()` is the terminal-facing orchestration entrypoint.
- Side effects / outputs: Produces the file's main side effects or terminal outputs.

