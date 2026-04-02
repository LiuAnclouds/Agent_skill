# Module Guide: `experiment/training/run_xgb_covshift.py`

## Purpose

GPU XGBoost exploration script for covariate-shift weighting between time-split train and val distributions.

## When To Read This File

Read this file when testing unsupervised covariate-shift weighting between phase1 train and val.

## Upstream Callers / Entrypoints

- shell / terminal

## Downstream Consumers / Artifacts

- xgboost_gpu/<run_name>/ summary and predictions

## Main Outputs Or Side Effects

- domain_model.json
- model.json
- prediction npz files

## Common Edit Hotspots

- Domain classifier design and sample-weighting logic live here.

## Top-Level Symbols

### `parse_args() -> argparse.Namespace`

- Kind: `function`
- Lines: `28-60`
- Role: CLI argument parser for this module.
- How to use: Called automatically by `main()` to define the user-facing CLI contract.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_slice_node_ids(node_ids: np.ndarray, limit: int | None, seed: int) -> np.ndarray`

- Kind: `function`
- Lines: `63-68`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_load_feature_slices(feature_dir: Path, feature_model: str, train_ids: np.ndarray, val_ids: np.ndarray, external_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]`

- Kind: `function`
- Lines: `71-84`
- Role: Load helper that restores data, configuration, or saved artifacts from disk.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `_booster_params(args: argparse.Namespace, scale_pos_weight: float) -> dict[str, float | int | str]`

- Kind: `function`
- Lines: `87-106`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_domain_params(args: argparse.Namespace) -> dict[str, float | int | str]`

- Kind: `function`
- Lines: `109-127`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `main() -> None`

- Kind: `function`
- Lines: `130-243`
- Role: Train a domain classifier between train and val, derive sample weights, and train a weighted CUDA XGBoost fraud model.
- How to use: Run this through the file's CLI command; `main()` is the terminal-facing orchestration entrypoint.
- Side effects / outputs: Produces the file's main side effects or terminal outputs.

