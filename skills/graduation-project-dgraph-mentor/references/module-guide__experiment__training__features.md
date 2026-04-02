# Module Guide: `experiment/training/features.py`

## Purpose

Offline feature-cache and graph-cache builder plus runtime FeatureStore and GraphCache readers.

## When To Read This File

Read this file before touching model input features, feature normalization, graph cache layout, or any offline build logic.

## Upstream Callers / Entrypoints

- experiment/training/run_training.py build_features
- experiment/training/run_xgb_graphprop.py
- experiment/training/run_xgb_relmean.py
- experiment/training/run_xgb_covshift.py

## Downstream Consumers / Artifacts

- FeatureStore consumers in gbdt_models.py and gnn_models.py
- experiment/outputs/training/features/

## Main Outputs Or Side Effects

- core_features.npy
- neighbor_features.npy
- feature_manifest.json
- graph/*.npy

## Common Edit Hotspots

- Add or remove feature groups here.
- If you change cache layout, update every reader that depends on FeatureStore or GraphCache.

## Top-Level Symbols

### `GraphCache`

- Kind: `class`
- Lines: `25-41`
- Role: Runtime bundle of CSR-like in/out adjacency arrays, edge metadata, and time-bucket annotations.
- How to use: Construct or load it once, then pass it downstream instead of repeatedly rebuilding the same context.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.

### `HybridFeatureNormalizerState`

- Kind: `class`
- Lines: `45-92`
- Role: Serializable description of how hybrid feature normalization should be applied at training and inference time.
- How to use: Read its fields or methods from the surrounding pipeline; this class is usually not invoked directly from the shell.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `to_dict(self) -> dict[str, Any]` lines `59-73`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Serialize the current object into a JSON-safe dict for checkpoints or summaries.
  - `from_dict(cls, payload: dict[str, Any] | None) -> HybridFeatureNormalizerState | None` lines `76-92`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Reconstruct the object from saved metadata when reloading a run.

### `FeatureStore`

- Kind: `class`
- Lines: `96-158`
- Role: Memmap-backed feature reader that assembles selected feature groups by node id.
- How to use: Read its fields or methods from the surrounding pipeline; this class is usually not invoked directly from the shell.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, phase: str, selected_groups: list[str], outdir: Path = FEATURE_OUTPUT_ROOT, normalizer_state: HybridFeatureNormalizerState | None = None) -> None` lines `97-119`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.
  - `_resolve_group_specs(self, selected_groups: list[str]) -> list[dict[str, Any]]` lines `121-139`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use this while working on feature extraction or cache reading inside `experiment/training/features.py`.
  - `take_rows(self, node_ids: np.ndarray) -> np.ndarray` lines `141-154`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use this while working on feature extraction or cache reading inside `experiment/training/features.py`.
  - `input_dim(self) -> int` lines `157-158`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use this while working on feature extraction or cache reading inside `experiment/training/features.py`.

### `_build_edge_time_windows(timestamps: np.ndarray, n_windows: int = NUM_TIME_WINDOWS) -> list[dict[str, int]]`

- Kind: `function`
- Lines: `161-182`
- Role: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `_assign_node_time_bucket(first_active: np.ndarray, time_windows: list[dict[str, int]]) -> np.ndarray`

- Kind: `function`
- Lines: `185-193`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_group_definition() -> tuple[dict[str, list[str]], dict[str, list[str]]]`

- Kind: `function`
- Lines: `196-261`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_allocate_group_spans(groups: dict[str, list[str]]) -> dict[str, dict[str, Any]]`

- Kind: `function`
- Lines: `264-274`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_write_graph_arrays(phase_dir: Path, prefix: str, centers: np.ndarray, neighbors: np.ndarray, edge_type: np.ndarray, edge_timestamp: np.ndarray, num_nodes: int) -> dict[str, str]`

- Kind: `function`
- Lines: `277-308`
- Role: Artifact-writing helper used to persist outputs for later reuse.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_bincount_float(indices: np.ndarray, weights: np.ndarray, size: int) -> np.ndarray`

- Kind: `function`
- Lines: `311-312`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_stable_std(value: float) -> float`

- Kind: `function`
- Lines: `315-316`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_feature_normalization_type(feature_name: str) -> str`

- Kind: `function`
- Lines: `319-345`
- Role: Private helper used internally by this module; read together with its callers.
- How to use: Use this while working on feature extraction or cache reading inside `experiment/training/features.py`.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `apply_hybrid_feature_normalizer(features: np.ndarray, state: HybridFeatureNormalizerState) -> np.ndarray`

- Kind: `function`
- Lines: `348-378`
- Role: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- How to use: Use this while working on feature extraction or cache reading inside `experiment/training/features.py`.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `build_hybrid_feature_normalizer(phase: str, selected_groups: list[str], train_ids: np.ndarray, outdir: Path = FEATURE_OUTPUT_ROOT) -> HybridFeatureNormalizerState`

- Kind: `function`
- Lines: `381-457`
- Role: Fit the hybrid normalization statistics from the phase1 train split only.
- How to use: Use this when you need to construct the next artifact bundle or derived object before training or reporting.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `_build_neighbor_features(data: PhaseData, phase_dir: Path, indegree: np.ndarray, outdegree: np.ndarray, x: np.ndarray, missing_mask: np.ndarray) -> tuple[str, dict[str, dict[str, Any]]]`

- Kind: `function`
- Lines: `460-513`
- Role: Construct the offline 1-hop neighbor aggregation blocks used by the m3 neighbor feature set.
- How to use: Internal builder used by the parent public function; modify it when changing how that artifact is assembled.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `build_phase_feature_artifacts(phase: str, outdir: Path = FEATURE_OUTPUT_ROOT, build_neighbor: bool = True) -> dict[str, Any]`

- Kind: `function`
- Lines: `516-710`
- Role: Core offline build path for one phase: core features, optional neighbor features, graph cache, and manifest.
- How to use: Use this when you need to construct the next artifact bundle or derived object before training or reporting.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `build_feature_artifacts(phases: list[str], outdir: Path = FEATURE_OUTPUT_ROOT, build_neighbor: bool = True) -> dict[str, Any]`

- Kind: `function`
- Lines: `713-732`
- Role: Multi-phase wrapper around build_phase_feature_artifacts().
- How to use: Use this when you need to construct the next artifact bundle or derived object before training or reporting.
- Side effects / outputs: Creates a derived bundle that later stages consume; may also write cache files.

### `load_feature_manifest(phase: str, outdir: Path = FEATURE_OUTPUT_ROOT) -> dict[str, Any]`

- Kind: `function`
- Lines: `735-736`
- Role: Read feature_manifest.json for one phase.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `load_graph_cache(phase: str, outdir: Path = FEATURE_OUTPUT_ROOT) -> GraphCache`

- Kind: `function`
- Lines: `739-763`
- Role: Open the graph cache arrays for one phase as memmaps.
- How to use: Use this to restore cached arrays, saved predictions, or configuration from disk.
- Side effects / outputs: Reads cached state from disk but should not change model parameters.

### `default_feature_groups(model_name: str) -> list[str]`

- Kind: `function`
- Lines: `766-784`
- Role: Map each model family name to its default feature-group recipe.
- How to use: Use this while working on feature extraction or cache reading inside `experiment/training/features.py`.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

