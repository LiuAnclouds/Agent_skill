# Module Guide: `experiment/training/run_xgb_multiclass_bg_scoreprop.py`

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
- Lines: `38-131`
- Role: CLI argument parser for this module.
- How to use: Called automatically by `main()` to define the user-facing CLI contract.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_cache_key(args: argparse.Namespace, threshold_day: int) -> str`

- Kind: `function`
- Lines: `134-163`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_make_xgb_params(args: argparse.Namespace) -> dict[str, float | int | str]`

- Kind: `function`
- Lines: `166-183`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_build_feature_store(feature_dir: Path, phase: str, feature_model: str, extra_groups: list[str]) -> FeatureStore`

- Kind: `function`
- Lines: `186-191`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `_take_rows(feature_store: FeatureStore, node_ids: np.ndarray) -> np.ndarray`

- Kind: `function`
- Lines: `194-195`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_predict_full_softprob(booster, feature_store: FeatureStore, predict_batch_size: int, best_iteration: int) -> np.ndarray`

- Kind: `function`
- Lines: `198-222`
- Role: Inference helper that converts a fitted model into fraud probabilities or scores.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_score_feature_names() -> list[str]`

- Kind: `function`
- Lines: `225-238`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_make_score_features(prob: np.ndarray) -> np.ndarray`

- Kind: `function`
- Lines: `241-261`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_multiclass_binary_auc_ignore_background(predt: np.ndarray, dmatrix) -> tuple[str, float]`

- Kind: `function`
- Lines: `264-272`
- Role: Metric helper used to evaluate fraud-detection predictions.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_load_or_build_stage1_probabilities(args: argparse.Namespace, cache_dir: Path, x_train: np.ndarray, y_train: np.ndarray, train_first_active: np.ndarray, threshold_day: int, x_val: np.ndarray, y_val: np.ndarray, phase1_store: FeatureStore, phase2_store: FeatureStore, historical_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]`

- Kind: `function`
- Lines: `275-398`
- Role: Load helper that restores data, configuration, or saved artifacts from disk.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `_append_feature_block(blocks: dict[str, list[np.ndarray]], feature_names: list[str], split_ids: dict[str, np.ndarray], full_matrix: np.ndarray, names: list[str], prefix: str) -> None`

- Kind: `function`
- Lines: `401-411`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_append_propagated_score_blocks(blocks: dict[str, list[np.ndarray]], feature_names: list[str], split_ids: dict[str, np.ndarray], score_matrix: np.ndarray, score_names: list[str], graph_cache, prop_blocks: list[str], prop_half_life_days: list[float | None]) -> None`

- Kind: `function`
- Lines: `414-477`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_write_feature_importance(booster, feature_names: list[str], path: Path) -> None`

- Kind: `function`
- Lines: `480-490`
- Role: Artifact-writing helper used to persist outputs for later reuse.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `main() -> None`

- Kind: `function`
- Lines: `493-685`
- Role: Module entrypoint that orchestrates the main workflow.
- How to use: Run this through the file's CLI command; `main()` is the terminal-facing orchestration entrypoint.
- Side effects / outputs: Produces the file's main side effects or terminal outputs.

