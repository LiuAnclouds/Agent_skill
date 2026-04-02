# Module Guide: `experiment/training/run_xgb_graphprop.py`

## Purpose

GPU XGBoost exploration script for propagated graph features such as A*X and A^2*X style blocks.

## When To Read This File

Read this file when exploring graph-propagated tabular feature blocks with CUDA XGBoost.

## Upstream Callers / Entrypoints

- shell / terminal

## Downstream Consumers / Artifacts

- xgboost_gpu/<run_name>/ summary and predictions

## Main Outputs Or Side Effects

- summary.json
- phase1_val_predictions.npz
- phase2_external_predictions.npz

## Common Edit Hotspots

- Graph-propagation feature recipes and caching strategy live here.

## Top-Level Symbols

### `parse_args() -> argparse.Namespace`

- Kind: `function`
- Lines: `33-127`
- Role: CLI argument parser for this module.
- How to use: Called automatically by `main()` to define the user-facing CLI contract.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_slice_node_ids(node_ids: np.ndarray, limit: int | None, seed: int) -> np.ndarray`

- Kind: `function`
- Lines: `130-135`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_cache_key(args: argparse.Namespace) -> str`

- Kind: `function`
- Lines: `138-154`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_resolve_half_lives(raw_values: list[float] | None) -> list[float | None]`

- Kind: `function`
- Lines: `157-171`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_resolve_model_extra_groups(args: argparse.Namespace, prefix: str) -> list[str]`

- Kind: `function`
- Lines: `174-178`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_half_life_tag(half_life_days: float | None) -> str`

- Kind: `function`
- Lines: `181-186`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_normalized_csr(ptr: np.ndarray, neighbors: np.ndarray, num_nodes: int, timestamps: np.ndarray | None = None, max_day: int | None = None, half_life_days: float | None = None) -> sp.csr_matrix`

- Kind: `function`
- Lines: `189-219`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_take_full_matrix(feature_dir: Path, phase: str, model_name: str, extra_groups: list[str] | None = None) -> tuple[np.ndarray, list[str]]`

- Kind: `function`
- Lines: `222-235`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_append_slices(blocks: dict[str, list[np.ndarray]], name_blocks: list[str], full_matrix: np.ndarray, full_feature_names: list[str], split_ids: dict[str, np.ndarray], prefix: str) -> None`

- Kind: `function`
- Lines: `238-249`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_build_phase_feature_blocks(phase: str, feature_dir: Path, base_model: str, prop_model: str, prop_blocks: list[str], base_extra_groups: list[str], prop_extra_groups: list[str], prop_half_life_days: list[float | None], split_ids: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], list[str]]`

- Kind: `function`
- Lines: `252-429`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `_load_or_build_cached_features(args: argparse.Namespace, cache_dir: Path, phase1_ids: dict[str, np.ndarray], phase2_ids: dict[str, np.ndarray], half_lives: list[float | None]) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], list[str]]`

- Kind: `function`
- Lines: `432-495`
- Role: Load helper that restores data, configuration, or saved artifacts from disk.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `_write_feature_importance(booster: Any, feature_names: list[str], path: Path) -> None`

- Kind: `function`
- Lines: `498-512`
- Role: Artifact-writing helper used to persist outputs for later reuse.
- How to use: Use this while working on feature extraction or cache reading inside `experiment/training/run_xgb_graphprop.py`.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `main() -> None`

- Kind: `function`
- Lines: `515-627`
- Role: Build propagated graph-feature blocks, train CUDA XGBoost, and save the resulting leaderboard artifact.
- How to use: Run this through the file's CLI command; `main()` is the terminal-facing orchestration entrypoint.
- Side effects / outputs: Produces the file's main side effects or terminal outputs.

