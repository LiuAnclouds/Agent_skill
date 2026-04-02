# Module Guide: `experiment/training/common.py`

## Purpose

Shared training utilities for paths, metrics, split loading, seeding, prediction saving, and device resolution.

## When To Read This File

Read this file when a training change needs new shared metrics, new split loading, or reusable IO helpers.

## Upstream Callers / Entrypoints

- experiment/training/run_training.py
- experiment/training/gbdt_models.py
- experiment/training/gnn_models.py
- experiment/training/run_xgb_*.py

## Downstream Consumers / Artifacts

- All training summaries, predictions, and metric calculations

## Main Outputs Or Side Effects

- Metric dicts, split bundles, prediction npz files

## Common Edit Hotspots

- Add new evaluation metrics here if all training flows should report them.
- Do not silently change load_experiment_split unless the evaluation contract changes everywhere.

## Top-Level Symbols

### `ExperimentSplit`

- Kind: `class`
- Lines: `24-29`
- Role: Container for the recommended phase1 train/val ids plus the phase2 external evaluation ids.
- How to use: Read its fields or methods from the surrounding pipeline; this class is usually not invoked directly from the shell.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.

### `ensure_dir(path: Path) -> Path`

- Kind: `function`
- Lines: `32-34`
- Role: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `write_json(path: Path, payload: dict[str, Any]) -> None`

- Kind: `function`
- Lines: `37-39`
- Role: Artifact-writing helper used to persist outputs for later reuse.
- How to use: Use this to persist artifacts so later stages can reuse them without recomputation.
- Side effects / outputs: Writes files to disk as its main side effect.

### `read_json(path: Path) -> dict[str, Any]`

- Kind: `function`
- Lines: `42-43`
- Role: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `set_global_seed(seed: int) -> None`

- Kind: `function`
- Lines: `46-56`
- Role: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `safe_auc(y_true: np.ndarray, y_score: np.ndarray) -> float`

- Kind: `function`
- Lines: `59-65`
- Role: Metric helper used to evaluate fraud-detection predictions.
- How to use: Call this when you need a deterministic derived statistic or robust evaluation metric.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `safe_average_precision(y_true: np.ndarray, y_score: np.ndarray) -> float`

- Kind: `function`
- Lines: `68-74`
- Role: Metric helper used to evaluate fraud-detection predictions.
- How to use: Call this when you need a deterministic derived statistic or robust evaluation metric.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `safe_pr_auc(y_true: np.ndarray, y_score: np.ndarray) -> float`

- Kind: `function`
- Lines: `77-84`
- Role: Metric helper used to evaluate fraud-detection predictions.
- How to use: Call this when you need a deterministic derived statistic or robust evaluation metric.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `compute_binary_classification_metrics(y_true: np.ndarray, y_score: np.ndarray) -> dict[str, float]`

- Kind: `function`
- Lines: `87-95`
- Role: Compute ROC-AUC, AP, and PR-AUC for binary fraud detection outputs.
- How to use: Call this when you need a deterministic derived statistic or robust evaluation metric.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `load_experiment_split(eda_root: Path = EDA_OUTPUT_ROOT) -> ExperimentSplit`

- Kind: `function`
- Lines: `98-108`
- Role: Load the persisted time-aware split built during EDA.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `load_phase_arrays(phase: str, keys: tuple[str, ...] = ('y', 'train_mask', 'test_mask')) -> dict[str, np.ndarray]`

- Kind: `function`
- Lines: `111-123`
- Role: Read selected arrays such as y/train_mask/test_mask directly from a phase npz file.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `slice_node_ids(node_ids: np.ndarray, limit: int | None, seed: int) -> np.ndarray`

- Kind: `function`
- Lines: `126-131`
- Role: Optional random subsampling helper for smoke tests or reduced-size runs.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `save_prediction_npz(path: Path, node_ids: np.ndarray, y_true: np.ndarray, probabilities: np.ndarray) -> None`

- Kind: `function`
- Lines: `134-146`
- Role: Persist node ids, labels, and probabilities into a compact npz artifact.
- How to use: Use this to persist artifacts so later stages can reuse them without recomputation.
- Side effects / outputs: Writes files to disk as its main side effect.

### `resolve_device(requested: str | None = None) -> str`

- Kind: `function`
- Lines: `149-157`
- Role: Choose the requested torch device or default to CUDA when available.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

