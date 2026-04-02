# Experiment Code Map

This document is generated from the live repository. It focuses on `experiment/` because that is the benchmark and thesis core.

Use this file as the fast index. For deeper per-file explanations, jump to `references/module-guides-index.md` and then open the guide for the target module.

## `experiment/eda/analysis.py`

Purpose: Run the reproducible EDA stack: overview, feature profile, graph statistics, temporal behavior, drift checks, and the recommended time-aware split.

When to read: Read this file when you need to understand where the recommended train/val split comes from, why the current validation regime is time-aware, or how the generated EDA artifacts are produced.

Inventory summary: 0 classes, 24 top-level functions, 0 documented methods.

Top-level symbols:
- `configure_matplotlib() -> None` [function] lines 25-33: Set a font stack that can render Chinese labels in generated plots and keep minus signs readable.
- `ensure_dir(path: Path) -> Path` [function] lines 36-38: Create an artifact directory if missing and return the same path for chained writes.
- `write_csv(path: Path, rows: list[dict[str, Any]]) -> None` [function] lines 41-56: Write a list of dict rows into a UTF-8 CSV artifact with stable field ordering.
- `write_json(path: Path, payload: dict[str, Any]) -> None` [function] lines 59-64: Persist a JSON summary artifact for later reuse by training or reporting code.
- `write_square_csv(path: Path, headers: list[str], matrix: np.ndarray) -> None` [function] lines 67-73: Write a square matrix such as a correlation or PSI-style table with row and column headers.
- `label_name(label: int) -> str` [function] lines 76-77: Map numeric dataset labels to readable names like normal, fraud, and background classes.
- `quantile_row(prefix: str, values: np.ndarray) -> dict[str, float]` [function] lines 80-86: Convert one numeric vector into a prefixed quantile-stat dict row for CSV summaries.
- `basic_stats(values: np.ndarray) -> dict[str, float]` [function] lines 89-97: Return a compact statistics dict used inside EDA summaries.
- `sample_values(values: np.ndarray, seed: int, max_size: int = PLOT_SAMPLE_SIZE) -> np.ndarray` [function] lines 100-105: Downsample large vectors for plotting so EDA remains tractable on million-scale data.
- `plot_empirical_cdf(ax: plt.Axes, values: np.ndarray, label: str, color: str) -> None` [function] lines 108-114: Draw an empirical CDF curve on an existing matplotlib axis.
- `build_time_windows(values: np.ndarray, n_windows: int = TIME_WINDOW_COUNT) -> list[dict[str, Any]]` [function] lines 117-139: Split a time-like vector into quantile-based windows for later temporal summaries.
- `build_phase_output_dir(outdir: Path, phase: str) -> Path` [function] lines 142-143: Create the output subdirectory for a specific phase under the EDA output root.
- `get_train_target(data: PhaseData) -> tuple[np.ndarray, np.ndarray]` [function] lines 146-148: Return the official supervised node ids and labels for one dataset phase.
- `analyze_overview(data: PhaseData, outdir: Path) -> dict[str, Any]` [function] lines 151-198: Produce the high-level size, label, edge-type, and train/test distribution summary for one phase.
- `analyze_features(data: PhaseData, outdir: Path, temporal_core: dict[str, np.ndarray] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]` [function] lines 201-457: Profile raw feature distributions, missingness, normal-vs-fraud gaps, and per-group missing patterns.
- `compute_degree_arrays(data: PhaseData) -> tuple[np.ndarray, np.ndarray, np.ndarray]` [function] lines 460-466: Compute indegree, outdegree, and total degree arrays from the raw edge list.
- `compute_temporal_core(data: PhaseData) -> dict[str, np.ndarray]` [function] lines 469-492: Compute first_active, last_active, and active_span arrays used throughout EDA and feature building.
- `analyze_graph(data: PhaseData, outdir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]` [function] lines 495-724: Profile graph structure, background-node effects, degree patterns, and edge-type behavior.
- `analyze_temporal(data: PhaseData, outdir: Path, temporal_core: dict[str, np.ndarray] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, np.ndarray]]` [function] lines 727-828: Profile node activity over time, time windows, and train-class temporal behavior.
- `_psi(reference: np.ndarray, current: np.ndarray, bins: np.ndarray) -> float` [function] lines 831-839: Compute a population stability style drift score between reference and current distributions.
- `_build_drift_bins(values: np.ndarray, n_bins: int = DRIFT_BIN_COUNT) -> np.ndarray` [function] lines 842-853: Create quantile-based bins for drift calculations.
- `analyze_drift(outdir: Path) -> tuple[list[dict[str, Any]], str]` [function] lines 856-946: Compare phase1 and phase2 feature drift and write a drift summary report.
- `build_recommended_split(outdir: Path, temporal_core: dict[str, np.ndarray] | None = None) -> dict[str, Any]` [function] lines 949-1022: Create the project's leakage-safe time-aware phase1 train/val split and phase2 external evaluation ids.
- `run_eda(phases: list[str], analyses: list[str], outdir: Path) -> dict[str, Any]` [function] lines 1025-1090: Execute the requested EDA stages, aggregate summaries, and persist the full artifact bundle.

## `experiment/eda/data_loader.py`

Purpose: Resolve the XinYe dataset paths, flatten arrays, validate schema assumptions, and load one phase into a typed PhaseData container.

When to read: Read this file first when dataset paths change or when the repository needs to support more datasets.

Inventory summary: 1 classes, 4 top-level functions, 2 documented methods.

Top-level symbols:
- `PhaseData` [class] lines 24-41: Immutable in-memory bundle for one dataset phase, including node features, labels, edges, timestamps, and official train/test node ids.
  - `num_nodes(self) -> int` [method] lines 36-37: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `num_edges(self) -> int` [method] lines 40-41: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `resolve_dataset_path(phase: str, repo_root: Path | None = None) -> Path` [function] lines 44-61: Find the canonical npz file for a named phase under the current dataset layout.
- `_flatten_array(values: np.ndarray, dtype: np.dtype | None = None) -> np.ndarray` [function] lines 64-68: Flatten label or mask arrays to one dimension and optionally cast dtype.
- `_validate_phase_data(data: PhaseData) -> None` [function] lines 71-100: Assert that the loaded phase matches the expected DGraph schema and label assumptions.
- `load_phase(phase: str, repo_root: Path | None = None) -> PhaseData` [function] lines 103-119: Load one dataset phase from disk and return a validated PhaseData object.

## `experiment/eda/run_eda.py`

Purpose: CLI entrypoint for the EDA pipeline.

When to read: Read this file when you need the exact EDA CLI surface or want to add a new user-facing EDA command-line option.

Inventory summary: 0 classes, 2 top-level functions, 0 documented methods.

Top-level symbols:
- `parse_args() -> argparse.Namespace` [function] lines 15-38: Parse CLI flags for phase selection, analysis modules, and output directory.
- `main() -> None` [function] lines 41-46: Entrypoint that expands phase selection and launches run_eda().

## `experiment/training/common.py`

Purpose: Shared training utilities for paths, metrics, split loading, seeding, prediction saving, and device resolution.

When to read: Read this file when a training change needs new shared metrics, new split loading, or reusable IO helpers.

Inventory summary: 1 classes, 13 top-level functions, 0 documented methods.

Top-level symbols:
- `ExperimentSplit` [class] lines 24-29: Container for the recommended phase1 train/val ids plus the phase2 external evaluation ids.
- `ensure_dir(path: Path) -> Path` [function] lines 32-34: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `write_json(path: Path, payload: dict[str, Any]) -> None` [function] lines 37-39: Artifact-writing helper used to persist outputs for later reuse.
- `read_json(path: Path) -> dict[str, Any]` [function] lines 42-43: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `set_global_seed(seed: int) -> None` [function] lines 46-56: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `safe_auc(y_true: np.ndarray, y_score: np.ndarray) -> float` [function] lines 59-65: Metric helper used to evaluate fraud-detection predictions.
- `safe_average_precision(y_true: np.ndarray, y_score: np.ndarray) -> float` [function] lines 68-74: Metric helper used to evaluate fraud-detection predictions.
- `safe_pr_auc(y_true: np.ndarray, y_score: np.ndarray) -> float` [function] lines 77-84: Metric helper used to evaluate fraud-detection predictions.
- `compute_binary_classification_metrics(y_true: np.ndarray, y_score: np.ndarray) -> dict[str, float]` [function] lines 87-95: Compute ROC-AUC, AP, and PR-AUC for binary fraud detection outputs.
- `load_experiment_split(eda_root: Path = EDA_OUTPUT_ROOT) -> ExperimentSplit` [function] lines 98-108: Load the persisted time-aware split built during EDA.
- `load_phase_arrays(phase: str, keys: tuple[str, ...] = ('y', 'train_mask', 'test_mask')) -> dict[str, np.ndarray]` [function] lines 111-123: Read selected arrays such as y/train_mask/test_mask directly from a phase npz file.
- `slice_node_ids(node_ids: np.ndarray, limit: int | None, seed: int) -> np.ndarray` [function] lines 126-131: Optional random subsampling helper for smoke tests or reduced-size runs.
- `save_prediction_npz(path: Path, node_ids: np.ndarray, y_true: np.ndarray, probabilities: np.ndarray) -> None` [function] lines 134-146: Persist node ids, labels, and probabilities into a compact npz artifact.
- `resolve_device(requested: str | None = None) -> str` [function] lines 149-157: Choose the requested torch device or default to CUDA when available.

## `experiment/training/features.py`

Purpose: Offline feature-cache and graph-cache builder plus runtime FeatureStore and GraphCache readers.

When to read: Read this file before touching model input features, feature normalization, graph cache layout, or any offline build logic.

Inventory summary: 3 classes, 25 top-level functions, 6 documented methods.

Top-level symbols:
- `GraphCache` [class] lines 31-47: Runtime bundle of CSR-like in/out adjacency arrays, edge metadata, and time-bucket annotations.
- `HybridFeatureNormalizerState` [class] lines 51-98: Serializable description of how hybrid feature normalization should be applied at training and inference time.
  - `to_dict(self) -> dict[str, Any]` [method] lines 65-79: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `from_dict(cls, payload: dict[str, Any] | None) -> HybridFeatureNormalizerState | None` [method] lines 82-98: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `FeatureStore` [class] lines 102-164: Memmap-backed feature reader that assembles selected feature groups by node id.
  - `__init__(self, phase: str, selected_groups: list[str], outdir: Path = FEATURE_OUTPUT_ROOT, normalizer_state: HybridFeatureNormalizerState | None = None) -> None` [method] lines 103-125: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_resolve_group_specs(self, selected_groups: list[str]) -> list[dict[str, Any]]` [method] lines 127-145: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `take_rows(self, node_ids: np.ndarray) -> np.ndarray` [method] lines 147-160: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `input_dim(self) -> int` [method] lines 163-164: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `_build_edge_time_windows(timestamps: np.ndarray, n_windows: int = NUM_TIME_WINDOWS) -> list[dict[str, int]]` [function] lines 167-188: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_assign_node_time_bucket(first_active: np.ndarray, time_windows: list[dict[str, int]]) -> np.ndarray` [function] lines 191-199: Private helper used internally by this module; read together with its callers.
- `_group_definition() -> tuple[dict[str, list[str]], dict[str, list[str]]]` [function] lines 202-390: Private helper used internally by this module; read together with its callers.
- `_allocate_group_spans(groups: dict[str, list[str]]) -> dict[str, dict[str, Any]]` [function] lines 393-403: Private helper used internally by this module; read together with its callers.
- `_write_graph_arrays(phase_dir: Path, prefix: str, centers: np.ndarray, neighbors: np.ndarray, edge_type: np.ndarray, edge_timestamp: np.ndarray, num_nodes: int) -> dict[str, str]` [function] lines 406-437: Artifact-writing helper used to persist outputs for later reuse.
- `_bincount_float(indices: np.ndarray, weights: np.ndarray, size: int) -> np.ndarray` [function] lines 440-441: Private helper used internally by this module; read together with its callers.
- `_stable_std(value: float) -> float` [function] lines 444-445: Private helper used internally by this module; read together with its callers.
- `_feature_normalization_type(feature_name: str) -> str` [function] lines 448-503: Private helper used internally by this module; read together with its callers.
- `_safe_ratio(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray` [function] lines 506-507: Private helper used internally by this module; read together with its callers.
- `_bucketwise_zscore(values: np.ndarray, bucket_ids: np.ndarray, num_buckets: int, valid_mask: np.ndarray | None = None) -> np.ndarray` [function] lines 510-556: Private helper used internally by this module; read together with its callers.
- `_build_temporal_bucket_norm_feature_block(x: np.ndarray, missing_mask: np.ndarray, first_active: np.ndarray, indegree: np.ndarray, outdegree: np.ndarray, bg_in_count: np.ndarray, bg_out_count: np.ndarray) -> np.ndarray` [function] lines 559-623: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_build_temporal_safe_feature_blocks(data: PhaseData, time_windows: list[dict[str, int]], node_time_bucket: np.ndarray, first_active: np.ndarray, background_mask: np.ndarray) -> dict[str, np.ndarray]` [function] lines 626-753: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_build_activation_early_feature_block(data: PhaseData, first_active: np.ndarray, background_mask: np.ndarray) -> np.ndarray` [function] lines 756-820: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_build_temporal_neighbor_feature_block(data: PhaseData, time_windows: list[dict[str, int]], node_time_bucket: np.ndarray, x: np.ndarray, missing_mask: np.ndarray) -> np.ndarray` [function] lines 823-870: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_build_graph_stats_feature_block(data: PhaseData, indegree: np.ndarray, outdegree: np.ndarray) -> np.ndarray` [function] lines 873-969: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_build_neighbor_similarity_feature_block(x: np.ndarray, missing_mask: np.ndarray, src: np.ndarray, dst: np.ndarray, indegree: np.ndarray, outdegree: np.ndarray) -> np.ndarray` [function] lines 972-1010: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `apply_hybrid_feature_normalizer(features: np.ndarray, state: HybridFeatureNormalizerState) -> np.ndarray` [function] lines 1013-1043: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `build_hybrid_feature_normalizer(phase: str, selected_groups: list[str], train_ids: np.ndarray, outdir: Path = FEATURE_OUTPUT_ROOT) -> HybridFeatureNormalizerState` [function] lines 1046-1122: Fit the hybrid normalization statistics from the phase1 train split only.
- `_build_neighbor_features(data: PhaseData, phase_dir: Path, indegree: np.ndarray, outdegree: np.ndarray, x: np.ndarray, missing_mask: np.ndarray) -> tuple[str, dict[str, dict[str, Any]]]` [function] lines 1125-1178: Construct the offline 1-hop neighbor aggregation blocks used by the m3 neighbor feature set.
- `build_phase_feature_artifacts(phase: str, outdir: Path = FEATURE_OUTPUT_ROOT, build_neighbor: bool = True) -> dict[str, Any]` [function] lines 1181-1444: Core offline build path for one phase: core features, optional neighbor features, graph cache, and manifest.
- `build_feature_artifacts(phases: list[str], outdir: Path = FEATURE_OUTPUT_ROOT, build_neighbor: bool = True) -> dict[str, Any]` [function] lines 1447-1466: Multi-phase wrapper around build_phase_feature_artifacts().
- `load_feature_manifest(phase: str, outdir: Path = FEATURE_OUTPUT_ROOT) -> dict[str, Any]` [function] lines 1469-1470: Read feature_manifest.json for one phase.
- `load_graph_cache(phase: str, outdir: Path = FEATURE_OUTPUT_ROOT) -> GraphCache` [function] lines 1473-1497: Open the graph cache arrays for one phase as memmaps.
- `default_feature_groups(model_name: str) -> list[str]` [function] lines 1500-1518: Map each model family name to its default feature-group recipe.
- `resolve_feature_groups(model_name: str, extra_groups: list[str] | None = None) -> list[str]` [function] lines 1521-1529: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.

## `experiment/training/gbdt_models.py`

Purpose: LightGBM baseline wrapper used by the unified training CLI.

When to read: Read this file when changing the LightGBM baseline behavior inside the unified training CLI.

Inventory summary: 1 classes, 0 top-level functions, 6 documented methods.

Top-level symbols:
- `LightGBMExperiment` [class] lines 32-145: Wrapper around a LightGBM fraud classifier with fit/predict/save/load helpers aligned to this project.
  - `__init__(self, model_name: str, seed: int, feature_groups: list[str] | None = None, params: dict[str, Any] | None = None) -> None` [method] lines 33-48: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `fit(self, train_store: FeatureStore, train_ids: np.ndarray, train_labels: np.ndarray, val_ids: np.ndarray, val_labels: np.ndarray) -> dict[str, float]` [method] lines 50-88: Train the LightGBM baseline on the phase1 train split and early-stop on phase1 val AUC.
  - `predict_proba(self, feature_store: FeatureStore, node_ids: np.ndarray) -> np.ndarray` [method] lines 90-95: Return fraud probabilities for a node-id slice.
  - `save(self, run_dir: Path, feature_names: list[str]) -> None` [method] lines 97-112: Persist the fitted booster and feature-importance metadata.
  - `_write_feature_importance(self, path: Path, feature_names: list[str]) -> None` [method] lines 114-131: Artifact-writing helper used to persist outputs for later reuse.
  - `load(cls, run_dir: Path) -> 'LightGBMExperiment'` [method] lines 134-145: Restore a saved LightGBM experiment from disk.

## `experiment/training/gnn_models.py`

Purpose: Graph sampling, relation-aware message passing layers, temporal encoders, training loop, logging, hard-negative mining, and GNN inference wrappers.

When to read: Read this file when changing graph sampling, temporal handling, losses, hard negatives, the GNN backbone, logging, or inference behavior.

Inventory summary: 14 classes, 15 top-level functions, 42 documented methods.

Top-level symbols:
- `GraphPhaseContext` [class] lines 34-39: Bundle one phase's feature store, graph cache, and labels so GNN training code can pass context as one object.
- `GraphModelConfig` [class] lines 43-154: Serializable configuration object for sampling, loss, normalization, negative sampling, scheduler, and temporal sampling behavior.
  - `to_dict(self) -> dict[str, Any]` [method] lines 75-107: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `from_dict(cls, payload: dict[str, Any] | None) -> 'GraphModelConfig'` [method] lines 110-144: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `use_legacy_path(self) -> bool` [method] lines 146-154: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `SampledSubgraph` [class] lines 158-166: Container holding the local-node list, sampled edges, relation ids, timestamps, and local target indices for one subgraph batch.
- `TrainBatchStats` [class] lines 170-178: Per-batch summary values used in training logs such as sampled subgraph size and positive rate.
  - `positive_rate(self) -> float` [method] lines 177-178: Training helper that optimizes the current model on the project split.
- `_append_text_line(path: Path, line: str) -> None` [function] lines 181-185: Append one human-readable log line to a training log file.
- `_append_jsonl(path: Path, payload: dict[str, Any]) -> None` [function] lines 188-192: Append one JSON event line to a jsonl metrics file.
- `_write_history_csv(path: Path, rows: list[dict[str, Any]]) -> None` [function] lines 195-203: Materialize the accumulated epoch history as a CSV file.
- `_plot_training_curves(path: Path, rows: list[dict[str, Any]]) -> str | None` [function] lines 206-260: Render loss and metric curves from the stored epoch history.
- `_sample_edge_indices(edge_timestamp: np.ndarray, fanout: int, rng: np.random.Generator, snapshot_end: int | None, sampler: str = 'uniform', recent_window: int = 50, recent_ratio: float = 0.8, training: bool = True) -> np.ndarray` [function] lines 263-329: Choose legal edge indices for one frontier node under fanout and optional temporal cutoff constraints.
- `sample_relation_subgraph(graph: GraphCache, seed_nodes: np.ndarray, fanouts: list[int], rng: np.random.Generator, snapshot_end: int | None = None, sampler: str = 'uniform', recent_window: int = 50, recent_ratio: float = 0.8, training: bool = True) -> SampledSubgraph` [function] lines 332-464: Sample a relation-aware local subgraph around one batch of seed nodes.
- `_sample_single_seed_subgraph(graph: GraphCache, seed: int, fanouts: list[int], rng: np.random.Generator, snapshot_end: int | None = None, sampler: str = 'uniform', recent_window: int = 50, recent_ratio: float = 0.8, training: bool = True) -> SampledSubgraph` [function] lines 467-585: Fast path for single-seed meanmax pooling cases to reduce repeated list / dict construction.
- `sample_batched_relation_subgraphs(graph: GraphCache, seed_nodes: np.ndarray, fanouts: list[int], rng: np.random.Generator, snapshot_end: int | None = None, sampler: str = 'uniform', recent_window: int = 50, recent_ratio: float = 0.8, training: bool = True) -> SampledSubgraph` [function] lines 588-657: Sample multiple seed-node subgraphs together and pack them for batched processing.
- `TimeEncoder` [class] lines 660-670: Sinusoidal-like time encoding module used to inject edge-time information into temporal models.
  - `__init__(self, out_dim: int) -> None` [method] lines 661-667: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `forward(self, relative_time: torch.Tensor) -> torch.Tensor` [method] lines 669-670: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `SafeBatchNorm1d` [class] lines 673-681: BatchNorm wrapper that avoids pathological behavior on very small batches.
  - `__init__(self, dim: int) -> None` [method] lines 674-676: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `forward(self, x: torch.Tensor) -> torch.Tensor` [method] lines 678-681: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `_make_norm(kind: str, dim: int) -> nn.Module` [function] lines 684-689: Factory for layer norm, safe batch norm, or identity normalization.
- `_compute_grad_norm(parameters: Any) -> float` [function] lines 692-699: Measure gradient norm for monitoring and optional clipping diagnostics.
- `_focal_bce_with_logits(logits: torch.Tensor, targets: torch.Tensor, pos_weight: torch.Tensor | None, gamma: float, alpha: float) -> torch.Tensor` [function] lines 702-722: Compute the focal BCE variant used when focal loss is enabled.
- `_pairwise_ranking_loss(logits: torch.Tensor, targets: torch.Tensor, margin: float) -> torch.Tensor` [function] lines 725-735: Compute the ranking term used when ranking-enhanced losses are enabled.
- `_dirichlet_energy(x: torch.Tensor, edge_src: torch.Tensor, edge_dst: torch.Tensor) -> torch.Tensor` [function] lines 738-746: Compute a smoothness-style graph regularity diagnostic on embeddings.
- `_pool_mean_max(values: torch.Tensor, group_ids: torch.Tensor, num_groups: int) -> tuple[torch.Tensor, torch.Tensor]` [function] lines 749-789: Build the mean/max pooled subgraph head input for target-node or subgraph fusion logic.
- `_segment_softmax(scores: torch.Tensor, group_ids: torch.Tensor, num_groups: int) -> torch.Tensor` [function] lines 792-817: Compute softmax values inside grouped edge segments for attention-style aggregation.
- `RelationSAGELayer` [class] lines 820-861: Relation-aware SAGE message-passing layer used by the baseline GraphSAGE stack.
  - `__init__(self, in_dim: int, out_dim: int, num_relations: int, rel_dim: int, time_dim: int = 0) -> None` [method] lines 821-834: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `forward(self, x: torch.Tensor, edge_src: torch.Tensor, edge_dst: torch.Tensor, rel_ids: torch.Tensor, time_feature: torch.Tensor | None = None) -> torch.Tensor` [method] lines 836-861: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `ModernRelationBlock` [class] lines 864-948: Modernized relation block with residual / FFN / normalization options for temporal GraphSAGE variants.
  - `__init__(self, hidden_dim: int, edge_dim: int, dropout: float, norm: str, residual: bool, ffn: bool, edge_encoder: str) -> None` [method] lines 865-906: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `forward(self, x: torch.Tensor, edge_src: torch.Tensor, edge_dst: torch.Tensor, edge_emb: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]` [method] lines 908-948: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `ModernRelationAttentionBlock` [class] lines 951-1033: Attention-based relation block used by the temporal GAT variant.
  - `__init__(self, hidden_dim: int, edge_dim: int, dropout: float, norm: str, residual: bool, ffn: bool, edge_encoder: str) -> None` [method] lines 952-999: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `forward(self, x: torch.Tensor, edge_src: torch.Tensor, edge_dst: torch.Tensor, edge_emb: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]` [method] lines 1001-1033: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `RelationGraphSAGENetwork` [class] lines 1036-1339: Top-level neural network that stacks relation blocks and produces logits for target nodes.
  - `__init__(self, input_dim: int, hidden_dim: int, num_layers: int, num_relations: int, rel_dim: int, dropout: float, temporal: bool, model_config: GraphModelConfig, aggregator_type: str = 'sage') -> None` [method] lines 1037-1124: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_build_edge_embedding(self, x: torch.Tensor, rel_ids: torch.Tensor, edge_relative_time: torch.Tensor | None) -> tuple[torch.Tensor | None, torch.Tensor | None]` [method] lines 1126-1150: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
  - `_subgraph_stats(self, node_repr: torch.Tensor, target_local_idx: torch.Tensor, node_subgraph_id: torch.Tensor, edge_subgraph_id: torch.Tensor, edge_dst: torch.Tensor, rel_ids: torch.Tensor, edge_relative_time: torch.Tensor | None) -> torch.Tensor` [method] lines 1152-1211: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_forward_subgraph_head(self, node_repr: torch.Tensor, edge_repr: torch.Tensor, target_local_idx: torch.Tensor, node_subgraph_id: torch.Tensor | None, edge_subgraph_id: torch.Tensor | None, edge_dst: torch.Tensor, rel_ids: torch.Tensor, edge_relative_time: torch.Tensor | None) -> torch.Tensor` [method] lines 1213-1266: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `forward(self, x: torch.Tensor, edge_src: torch.Tensor, edge_dst: torch.Tensor, rel_ids: torch.Tensor, edge_relative_time: torch.Tensor | None, target_local_idx: torch.Tensor, node_subgraph_id: torch.Tensor | None = None, edge_subgraph_id: torch.Tensor | None = None, return_details: bool = False) -> torch.Tensor | tuple[torch.Tensor, dict[str, float]]` [method] lines 1268-1339: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `BaseGraphSAGEExperiment` [class] lines 1342-2495: Main training / inference wrapper for graph models, including batch building, hard negatives, losses, logging, save/load, and evaluation.
  - `__init__(self, model_name: str, seed: int, input_dim: int, num_relations: int, max_day: int, feature_groups: list[str] | None = None, hidden_dim: int = 128, num_layers: int = 2, rel_dim: int = 32, fanouts: list[int] | None = None, batch_size: int = 1024, epochs: int = 4, learning_rate: float = 0.001, weight_decay: float = 1e-05, dropout: float = 0.2, device: str | None = None, temporal: bool = False, aggregator_type: str = 'sage', graph_config: GraphModelConfig | None = None, feature_normalizer_state: HybridFeatureNormalizerState | None = None) -> None` [method] lines 1343-1399: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_hard_negative_pool_key(self, snapshot_end: int | None) -> int` [method] lines 1401-1402: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_hard_negative_enabled(self) -> bool` [method] lines 1404-1408: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_uses_ranking_loss(self) -> bool` [method] lines 1410-1411: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_iter_train_partitions(self, context: GraphPhaseContext, node_ids: np.ndarray) -> list[tuple[np.ndarray, np.ndarray, int | None]]` [method] lines 1413-1432: Training helper that optimizes the current model on the project split.
  - `_compute_loss(self, logits: torch.Tensor, targets: torch.Tensor, pos_weight: torch.Tensor) -> tuple[torch.Tensor, dict[str, float]]` [method] lines 1434-1469: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_current_hard_negative_pool_size(self) -> int` [method] lines 1471-1472: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_current_hard_negative_candidate_count(self) -> int` [method] lines 1474-1477: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_maybe_refresh_hard_negative_pools(self, context: GraphPhaseContext, train_ids: np.ndarray, epoch: int, rng: np.random.Generator) -> dict[str, int | bool]` [method] lines 1479-1588: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_sample_negative_partition(self, neg_nodes: np.ndarray, neg_positions: np.ndarray, sampled_negatives: int, snapshot_end: int | None, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, int]` [method] lines 1590-1711: Sampling helper used to create local subgraphs, negatives, or reduced node subsets.
  - `_iter_batches(self, context: GraphPhaseContext, node_ids: np.ndarray, training: bool, rng: np.random.Generator) -> list[tuple[np.ndarray, np.ndarray, int | None]]` [method] lines 1713-1757: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_chunk_batch_partition(self, nodes: np.ndarray, positions: np.ndarray, snapshot_end: int | None, effective_batch_size: int) -> list[tuple[np.ndarray, np.ndarray, int | None]]` [method] lines 1759-1773: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `_build_balanced_partition_batches(self, nodes: np.ndarray, positions: np.ndarray, labels: np.ndarray, snapshot_end: int | None, rng: np.random.Generator, effective_batch_size: int) -> tuple[list[tuple[np.ndarray, np.ndarray, int | None]], TrainBatchStats]` [method] lines 1775-1871: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
  - `_build_train_batches(self, context: GraphPhaseContext, node_ids: np.ndarray, rng: np.random.Generator) -> tuple[list[tuple[np.ndarray, np.ndarray, int | None]], TrainBatchStats]` [method] lines 1873-1931: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
  - `_sample_batch_subgraph(self, graph: GraphCache, batch_nodes: np.ndarray, rng: np.random.Generator, snapshot_end: int | None, training: bool) -> SampledSubgraph` [method] lines 1933-1957: Sampling helper used to create local subgraphs, negatives, or reduced node subsets.
  - `_tensorize_subgraph(self, context: GraphPhaseContext, subgraph: SampledSubgraph, snapshot_end: int | None) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor | None, torch.Tensor, torch.Tensor | None, torch.Tensor | None]` [method] lines 1959-2030: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
  - `fit(self, context: GraphPhaseContext, train_ids: np.ndarray, val_ids: np.ndarray, artifact_dir: Path | None = None) -> dict[str, float]` [method] lines 2032-2344: Run the full multi-epoch graph training loop, logging metrics and early-stopping on phase1 validation AUC.
  - `predict_proba(self, context: GraphPhaseContext, node_ids: np.ndarray, batch_seed: int | None = None, progress_desc: str | None = None, show_progress: bool = True) -> np.ndarray` [method] lines 2347-2417: Run batched subgraph inference and return probabilities for the requested node ids.
  - `save(self, run_dir: Path) -> None` [method] lines 2419-2446: Persist graph model weights and metadata.
  - `load(cls, run_dir: Path, input_dim: int, num_relations: int, device: str | None = None) -> 'BaseGraphSAGEExperiment'` [method] lines 2449-2495: Restore a saved graph experiment from disk.
- `RelationGraphSAGEExperiment` [class] lines 2498-2502: Concrete static relation GraphSAGE experiment wrapper.
  - `__init__(self, *args: Any, **kwargs: Any) -> None` [method] lines 2499-2502: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `TemporalRelationGraphSAGEExperiment` [class] lines 2505-2509: Concrete temporal GraphSAGE experiment wrapper.
  - `__init__(self, *args: Any, **kwargs: Any) -> None` [method] lines 2506-2509: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.
- `TemporalRelationGATExperiment` [class] lines 2512-2516: Concrete temporal relation attention experiment wrapper.
  - `__init__(self, *args: Any, **kwargs: Any) -> None` [method] lines 2513-2516: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.

## `experiment/training/run_training.py`

Purpose: Unified CLI for build_features, LightGBM / GNN training, and prediction blending.

When to read: Read this file when the user-facing training CLI changes, when a new model family is added to the main benchmark path, or when summary outputs need to change consistently.

Inventory summary: 0 classes, 18 top-level functions, 0 documented methods.

Top-level symbols:
- `_path_repr(path: Path) -> str` [function] lines 54-58: Private helper used internally by this module; read together with its callers.
- `parse_args() -> argparse.Namespace` [function] lines 61-405: Parse the unified CLI for feature building, tabular/GNN training, and blending.
- `_model_run_dir(outdir: Path, model_name: str, run_name: str) -> Path` [function] lines 408-409: Private helper used internally by this module; read together with its callers.
- `_load_labels_for_splits(split) -> tuple[np.ndarray, np.ndarray]` [function] lines 412-418: Load helper that restores data, configuration, or saved artifacts from disk.
- `_prepare_split_ids(args: argparse.Namespace)` [function] lines 421-426: Private helper used internally by this module; read together with its callers.
- `_build_graph_model_config(args: argparse.Namespace) -> GraphModelConfig` [function] lines 429-466: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_save_average_predictions(run_dir: Path, split_name: str, node_ids: np.ndarray, labels: np.ndarray, predictions: list[np.ndarray]) -> Path` [function] lines 469-479: Artifact-writing helper used to persist outputs for later reuse.
- `_benchmark_summary_path(outdir: Path, run_name: str) -> Path` [function] lines 482-483: Private helper used internally by this module; read together with its callers.
- `_build_promotion_decision(model_name: str, run_name: str, outdir: Path, summary_payload: dict[str, Any]) -> dict[str, Any]` [function] lines 486-519: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `run_build_features(args: argparse.Namespace) -> None` [function] lines 522-530: Launch the offline feature and graph-cache build.
- `run_train_lightgbm(args: argparse.Namespace) -> None` [function] lines 533-663: Train tabular baselines on the recommended split and write per-seed plus averaged predictions.
- `_make_graph_contexts(feature_dir: Path, model_name: str, extra_groups: list[str] | None = None, feature_normalizer_state = None, phase1_known_label_codes: np.ndarray | None = None, phase2_known_label_codes: np.ndarray | None = None) -> tuple[GraphPhaseContext, GraphPhaseContext]` [function] lines 666-694: Open feature stores, graph caches, and labels for both phases.
- `run_train_graph(args: argparse.Namespace) -> None` [function] lines 697-904: Train GNN models, evaluate on phase1 val and phase2 external, and write logs / curves / summaries.
- `_load_prediction_bundle(path: Path) -> dict[str, np.ndarray]` [function] lines 907-913: Load helper that restores data, configuration, or saved artifacts from disk.
- `_logit(probability: np.ndarray) -> np.ndarray` [function] lines 916-918: Private helper used internally by this module; read together with its callers.
- `_resolve_prediction_path(model_run_dir: Path, split_name: str) -> Path` [function] lines 921-932: Inference helper that converts a fitted model into fraud probabilities or scores.
- `run_blend(args: argparse.Namespace) -> None` [function] lines 935-1020: Blend multiple saved model runs through logistic stacking on validation logits.
- `main() -> None` [function] lines 1023-1037: Top-level dispatcher for the unified training CLI.

## `experiment/training/run_xgb_covshift.py`

Purpose: GPU XGBoost exploration script for covariate-shift weighting between time-split train and val distributions.

When to read: Read this file when testing unsupervised covariate-shift weighting between phase1 train and val.

Inventory summary: 0 classes, 6 top-level functions, 0 documented methods.

Top-level symbols:
- `parse_args() -> argparse.Namespace` [function] lines 28-66: CLI argument parser for this module.
- `_slice_node_ids(node_ids: np.ndarray, limit: int | None, seed: int) -> np.ndarray` [function] lines 69-74: Private helper used internally by this module; read together with its callers.
- `_load_feature_slices(feature_dir: Path, feature_model: str, extra_groups: list[str] | None, train_ids: np.ndarray, val_ids: np.ndarray, external_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]` [function] lines 77-91: Load helper that restores data, configuration, or saved artifacts from disk.
- `_booster_params(args: argparse.Namespace, scale_pos_weight: float) -> dict[str, float | int | str]` [function] lines 94-113: Private helper used internally by this module; read together with its callers.
- `_domain_params(args: argparse.Namespace) -> dict[str, float | int | str]` [function] lines 116-134: Private helper used internally by this module; read together with its callers.
- `main() -> None` [function] lines 137-252: Train a domain classifier between train and val, derive sample weights, and train a weighted CUDA XGBoost fraud model.

## `experiment/training/run_xgb_graphprop.py`

Purpose: GPU XGBoost exploration script for propagated graph features such as A*X and A^2*X style blocks.

When to read: Read this file when exploring graph-propagated tabular feature blocks with CUDA XGBoost.

Inventory summary: 0 classes, 13 top-level functions, 0 documented methods.

Top-level symbols:
- `parse_args() -> argparse.Namespace` [function] lines 33-127: CLI argument parser for this module.
- `_slice_node_ids(node_ids: np.ndarray, limit: int | None, seed: int) -> np.ndarray` [function] lines 130-135: Private helper used internally by this module; read together with its callers.
- `_cache_key(args: argparse.Namespace) -> str` [function] lines 138-154: Private helper used internally by this module; read together with its callers.
- `_resolve_half_lives(raw_values: list[float] | None) -> list[float | None]` [function] lines 157-171: Private helper used internally by this module; read together with its callers.
- `_resolve_model_extra_groups(args: argparse.Namespace, prefix: str) -> list[str]` [function] lines 174-178: Private helper used internally by this module; read together with its callers.
- `_half_life_tag(half_life_days: float | None) -> str` [function] lines 181-186: Private helper used internally by this module; read together with its callers.
- `_normalized_csr(ptr: np.ndarray, neighbors: np.ndarray, num_nodes: int, timestamps: np.ndarray | None = None, max_day: int | None = None, half_life_days: float | None = None) -> sp.csr_matrix` [function] lines 189-219: Private helper used internally by this module; read together with its callers.
- `_take_full_matrix(feature_dir: Path, phase: str, model_name: str, extra_groups: list[str] | None = None) -> tuple[np.ndarray, list[str]]` [function] lines 222-235: Private helper used internally by this module; read together with its callers.
- `_append_slices(blocks: dict[str, list[np.ndarray]], name_blocks: list[str], full_matrix: np.ndarray, full_feature_names: list[str], split_ids: dict[str, np.ndarray], prefix: str) -> None` [function] lines 238-249: Private helper used internally by this module; read together with its callers.
- `_build_phase_feature_blocks(phase: str, feature_dir: Path, base_model: str, prop_model: str, prop_blocks: list[str], base_extra_groups: list[str], prop_extra_groups: list[str], prop_half_life_days: list[float | None], split_ids: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], list[str]]` [function] lines 252-429: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_load_or_build_cached_features(args: argparse.Namespace, cache_dir: Path, phase1_ids: dict[str, np.ndarray], phase2_ids: dict[str, np.ndarray], half_lives: list[float | None]) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], list[str]]` [function] lines 432-495: Load helper that restores data, configuration, or saved artifacts from disk.
- `_write_feature_importance(booster: Any, feature_names: list[str], path: Path) -> None` [function] lines 498-512: Artifact-writing helper used to persist outputs for later reuse.
- `main() -> None` [function] lines 515-627: Build propagated graph-feature blocks, train CUDA XGBoost, and save the resulting leaderboard artifact.

## `experiment/training/run_xgb_multiclass_bg.py`

Purpose: Project module inside experiment/.

Inventory summary: 0 classes, 7 top-level functions, 0 documented methods.

Top-level symbols:
- `parse_args() -> argparse.Namespace` [function] lines 29-98: CLI argument parser for this module.
- `_build_feature_matrices(feature_dir: Path, feature_model: str, extra_groups: list[str], train_ids: np.ndarray, val_ids: np.ndarray, external_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]` [function] lines 101-115: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_multiclass_binary_auc(predt: np.ndarray, dmatrix) -> tuple[str, float]` [function] lines 118-125: Metric helper used to evaluate fraud-detection predictions.
- `_binary_score_from_softprob(prob: np.ndarray) -> np.ndarray` [function] lines 128-130: Private helper used internally by this module; read together with its callers.
- `_build_sample_weight(y_train: np.ndarray, args: argparse.Namespace, train_first_active: np.ndarray | None = None, threshold_day: int | None = None) -> dict[str, float | dict[str, float]]` [function] lines 133-178: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_write_feature_importance(booster, feature_names: list[str], path: Path) -> None` [function] lines 181-200: Artifact-writing helper used to persist outputs for later reuse.
- `main() -> None` [function] lines 203-331: Module entrypoint that orchestrates the main workflow.

## `experiment/training/run_xgb_multiclass_bg_graphprop.py`

Purpose: Project module inside experiment/.

Inventory summary: 0 classes, 7 top-level functions, 0 documented methods.

Top-level symbols:
- `parse_args() -> argparse.Namespace` [function] lines 32-119: CLI argument parser for this module.
- `_cache_key(args: argparse.Namespace, threshold_day: int) -> str` [function] lines 122-139: Private helper used internally by this module; read together with its callers.
- `_multiclass_binary_auc(predt: np.ndarray, dmatrix) -> tuple[str, float]` [function] lines 142-149: Metric helper used to evaluate fraud-detection predictions.
- `_binary_score_from_softprob(prob: np.ndarray) -> np.ndarray` [function] lines 152-154: Private helper used internally by this module; read together with its callers.
- `_build_sample_weight(y_train: np.ndarray, args: argparse.Namespace, train_first_active: np.ndarray | None = None, threshold_day: int | None = None) -> dict[str, float | dict[str, float]]` [function] lines 157-202: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_write_feature_importance(booster, feature_names: list[str], path: Path) -> None` [function] lines 205-215: Artifact-writing helper used to persist outputs for later reuse.
- `main() -> None` [function] lines 218-369: Module entrypoint that orchestrates the main workflow.

## `experiment/training/run_xgb_multiclass_bg_scoreprop.py`

Purpose: Project module inside experiment/.

Inventory summary: 0 classes, 14 top-level functions, 0 documented methods.

Top-level symbols:
- `parse_args() -> argparse.Namespace` [function] lines 38-131: CLI argument parser for this module.
- `_cache_key(args: argparse.Namespace, threshold_day: int) -> str` [function] lines 134-163: Private helper used internally by this module; read together with its callers.
- `_make_xgb_params(args: argparse.Namespace) -> dict[str, float | int | str]` [function] lines 166-183: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_build_feature_store(feature_dir: Path, phase: str, feature_model: str, extra_groups: list[str]) -> FeatureStore` [function] lines 186-191: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_take_rows(feature_store: FeatureStore, node_ids: np.ndarray) -> np.ndarray` [function] lines 194-195: Private helper used internally by this module; read together with its callers.
- `_predict_full_softprob(booster, feature_store: FeatureStore, predict_batch_size: int, best_iteration: int) -> np.ndarray` [function] lines 198-222: Inference helper that converts a fitted model into fraud probabilities or scores.
- `_score_feature_names() -> list[str]` [function] lines 225-238: Private helper used internally by this module; read together with its callers.
- `_make_score_features(prob: np.ndarray) -> np.ndarray` [function] lines 241-261: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_multiclass_binary_auc_ignore_background(predt: np.ndarray, dmatrix) -> tuple[str, float]` [function] lines 264-272: Metric helper used to evaluate fraud-detection predictions.
- `_load_or_build_stage1_probabilities(args: argparse.Namespace, cache_dir: Path, x_train: np.ndarray, y_train: np.ndarray, train_first_active: np.ndarray, threshold_day: int, x_val: np.ndarray, y_val: np.ndarray, phase1_store: FeatureStore, phase2_store: FeatureStore, historical_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]` [function] lines 275-398: Load helper that restores data, configuration, or saved artifacts from disk.
- `_append_feature_block(blocks: dict[str, list[np.ndarray]], feature_names: list[str], split_ids: dict[str, np.ndarray], full_matrix: np.ndarray, names: list[str], prefix: str) -> None` [function] lines 401-411: Private helper used internally by this module; read together with its callers.
- `_append_propagated_score_blocks(blocks: dict[str, list[np.ndarray]], feature_names: list[str], split_ids: dict[str, np.ndarray], score_matrix: np.ndarray, score_names: list[str], graph_cache, prop_blocks: list[str], prop_half_life_days: list[float | None]) -> None` [function] lines 414-477: Private helper used internally by this module; read together with its callers.
- `_write_feature_importance(booster, feature_names: list[str], path: Path) -> None` [function] lines 480-490: Artifact-writing helper used to persist outputs for later reuse.
- `main() -> None` [function] lines 493-685: Module entrypoint that orchestrates the main workflow.

## `experiment/training/run_xgb_multiclass_bg_targetenc.py`

Purpose: Project module inside experiment/.

Inventory summary: 0 classes, 9 top-level functions, 0 documented methods.

Top-level symbols:
- `parse_args() -> argparse.Namespace` [function] lines 38-75: CLI argument parser for this module.
- `_load_raw_feature_rows(phase: str, node_ids: np.ndarray, feature_dir: Path) -> np.ndarray` [function] lines 78-87: Load helper that restores data, configuration, or saved artifacts from disk.
- `_stable_quantile_edges(values: np.ndarray, n_bins: int) -> np.ndarray` [function] lines 90-103: Private helper used internally by this module; read together with its callers.
- `_digitize_with_missing(values: np.ndarray, edges: np.ndarray) -> np.ndarray` [function] lines 106-111: Private helper used internally by this module; read together with its callers.
- `_safe_prob(numerator: np.ndarray, denominator: np.ndarray, prior: float, smoothing: float) -> np.ndarray` [function] lines 114-123: Private helper used internally by this module; read together with its callers.
- `_logit(prob: np.ndarray) -> np.ndarray` [function] lines 126-128: Private helper used internally by this module; read together with its callers.
- `_build_target_encoding_features(raw_train: np.ndarray, y_train: np.ndarray, raw_val: np.ndarray, raw_external: np.ndarray, n_bins: int, smoothing: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]` [function] lines 131-225: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_write_feature_importance(booster, feature_names: list[str], path: Path) -> None` [function] lines 228-242: Artifact-writing helper used to persist outputs for later reuse.
- `main() -> None` [function] lines 245-383: Module entrypoint that orchestrates the main workflow.

## `experiment/training/run_xgb_pseudo.py`

Purpose: Project module inside experiment/.

Inventory summary: 0 classes, 5 top-level functions, 0 documented methods.

Top-level symbols:
- `parse_args() -> argparse.Namespace` [function] lines 27-78: CLI argument parser for this module.
- `_load_prediction_bundle(path: Path) -> dict[str, np.ndarray]` [function] lines 81-87: Load helper that restores data, configuration, or saved artifacts from disk.
- `_prediction_path(run_dir: Path, split_name: str) -> Path` [function] lines 90-97: Inference helper that converts a fitted model into fraud probabilities or scores.
- `_select_pseudo_indices(probabilities: np.ndarray, pos_threshold: float, neg_threshold: float, neg_ratio_cap: float, max_nodes: int | None) -> tuple[np.ndarray, np.ndarray]` [function] lines 100-133: Private helper used internally by this module; read together with its callers.
- `main() -> None` [function] lines 136-283: Module entrypoint that orchestrates the main workflow.

## `experiment/training/run_xgb_relmean.py`

Purpose: GPU XGBoost exploration script for relation-specific neighbor mean features.

When to read: Read this file when exploring relation-specific neighbor mean features with CUDA XGBoost.

Inventory summary: 0 classes, 10 top-level functions, 0 documented methods.

Top-level symbols:
- `parse_args() -> argparse.Namespace` [function] lines 33-84: CLI argument parser for this module.
- `_slice_node_ids(node_ids: np.ndarray, limit: int | None, seed: int) -> np.ndarray` [function] lines 87-92: Private helper used internally by this module; read together with its callers.
- `_cache_key(args: argparse.Namespace) -> str` [function] lines 95-107: Private helper used internally by this module; read together with its callers.
- `_take_base_matrix(feature_dir: Path, phase: str, model_name: str, extra_groups: list[str] | None = None) -> tuple[np.ndarray, list[str]]` [function] lines 110-123: Private helper used internally by this module; read together with its callers.
- `_append_slices(split_blocks: dict[str, list[np.ndarray]], full_matrix: np.ndarray, split_ids: dict[str, np.ndarray]) -> None` [function] lines 126-132: Private helper used internally by this module; read together with its callers.
- `_build_relation_csr(centers: np.ndarray, neighbors: np.ndarray, num_nodes: int) -> sp.csr_matrix` [function] lines 135-145: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_build_phase_feature_blocks(phase: str, feature_dir: Path, base_model: str, extra_groups: list[str], edge_types: list[int], include_missing_ratio: bool, split_ids: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], list[str]]` [function] lines 148-220: Builder helper that assembles the next-stage object, feature block, or configuration bundle.
- `_load_or_build_cached_features(args: argparse.Namespace, cache_dir: Path, phase1_ids: dict[str, np.ndarray], phase2_ids: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], list[str]]` [function] lines 223-288: Load helper that restores data, configuration, or saved artifacts from disk.
- `_write_feature_importance(booster: Any, feature_names: list[str], path: Path) -> None` [function] lines 291-300: Artifact-writing helper used to persist outputs for later reuse.
- `main() -> None` [function] lines 303-405: Build relation-specific neighbor mean features, train CUDA XGBoost, and save the resulting leaderboard artifact.

