# Module Guide: `experiment/training/run_xgb_relmean.py`

## Purpose

GPU XGBoost exploration script for relation-specific neighbor mean features.

## When To Read This File

Read this file when exploring relation-specific neighbor mean features with CUDA XGBoost.

## Upstream Callers / Entrypoints

- shell / terminal

## Downstream Consumers / Artifacts

- xgboost_gpu/<run_name>/ summary and predictions

## Main Outputs Or Side Effects

- summary.json
- feature_importance.csv
- prediction npz files

## Common Edit Hotspots

- Per-edge-type aggregation logic and cache layout live here.

## Top-Level Symbols

### `parse_args() -> argparse.Namespace`

- Kind: `function`
- Lines: `33-78`
- Role: CLI argument parser for this module.
- How to use: Called automatically by `main()` to define the user-facing CLI contract.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_slice_node_ids(node_ids: np.ndarray, limit: int | None, seed: int) -> np.ndarray`

- Kind: `function`
- Lines: `81-86`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_cache_key(args: argparse.Namespace) -> str`

- Kind: `function`
- Lines: `89-100`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_take_base_matrix(feature_dir: Path, phase: str, model_name: str) -> tuple[np.ndarray, list[str]]`

- Kind: `function`
- Lines: `103-107`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_append_slices(split_blocks: dict[str, list[np.ndarray]], full_matrix: np.ndarray, split_ids: dict[str, np.ndarray]) -> None`

- Kind: `function`
- Lines: `110-116`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_build_relation_csr(centers: np.ndarray, neighbors: np.ndarray, num_nodes: int) -> sp.csr_matrix`

- Kind: `function`
- Lines: `119-129`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `_build_phase_feature_blocks(phase: str, feature_dir: Path, base_model: str, edge_types: list[int], include_missing_ratio: bool, split_ids: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], list[str]]`

- Kind: `function`
- Lines: `132-203`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `_load_or_build_cached_features(args: argparse.Namespace, cache_dir: Path, phase1_ids: dict[str, np.ndarray], phase2_ids: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], list[str]]`

- Kind: `function`
- Lines: `206-269`
- Role: Load helper that restores data, configuration, or saved artifacts from disk.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `_write_feature_importance(booster: Any, feature_names: list[str], path: Path) -> None`

- Kind: `function`
- Lines: `272-281`
- Role: Artifact-writing helper used to persist outputs for later reuse.
- How to use: Use this while working on feature extraction or cache reading inside `experiment/training/run_xgb_relmean.py`.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `main() -> None`

- Kind: `function`
- Lines: `284-385`
- Role: Build relation-specific neighbor mean features, train CUDA XGBoost, and save the resulting leaderboard artifact.
- How to use: Run this through the file's CLI command; `main()` is the terminal-facing orchestration entrypoint.
- Side effects / outputs: Produces the file's main side effects or terminal outputs.

