# Module Guide: `experiment/training/run_xgb_multiclass_bg_targetenc.py`

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
- Lines: `38-75`
- Role: CLI argument parser for this module.
- How to use: Called automatically by `main()` to define the user-facing CLI contract.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_load_raw_feature_rows(phase: str, node_ids: np.ndarray, feature_dir: Path) -> np.ndarray`

- Kind: `function`
- Lines: `78-87`
- Role: Load helper that restores data, configuration, or saved artifacts from disk.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `_stable_quantile_edges(values: np.ndarray, n_bins: int) -> np.ndarray`

- Kind: `function`
- Lines: `90-103`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_digitize_with_missing(values: np.ndarray, edges: np.ndarray) -> np.ndarray`

- Kind: `function`
- Lines: `106-111`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_safe_prob(numerator: np.ndarray, denominator: np.ndarray, prior: float, smoothing: float) -> np.ndarray`

- Kind: `function`
- Lines: `114-123`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_logit(prob: np.ndarray) -> np.ndarray`

- Kind: `function`
- Lines: `126-128`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_build_target_encoding_features(raw_train: np.ndarray, y_train: np.ndarray, raw_val: np.ndarray, raw_external: np.ndarray, n_bins: int, smoothing: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]`

- Kind: `function`
- Lines: `131-225`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `_write_feature_importance(booster, feature_names: list[str], path: Path) -> None`

- Kind: `function`
- Lines: `228-242`
- Role: Artifact-writing helper used to persist outputs for later reuse.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `main() -> None`

- Kind: `function`
- Lines: `245-383`
- Role: Module entrypoint that orchestrates the main workflow.
- How to use: Run this through the file's CLI command; `main()` is the terminal-facing orchestration entrypoint.
- Side effects / outputs: Produces the file's main side effects or terminal outputs.

