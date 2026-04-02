# Module Guide: `experiment/training/gnn_models.py`

## Purpose

Graph sampling, relation-aware message passing layers, temporal encoders, training loop, logging, hard-negative mining, and GNN inference wrappers.

## When To Read This File

Read this file when changing graph sampling, temporal handling, losses, hard negatives, the GNN backbone, logging, or inference behavior.

## Upstream Callers / Entrypoints

- experiment/training/run_training.py::run_train_graph

## Downstream Consumers / Artifacts

- Per-seed GNN artifacts under experiment/outputs/training/models/
- phase1 val and phase2 external probabilities

## Main Outputs Or Side Effects

- train.log
- epoch_metrics.csv / .jsonl
- training_curves.png
- model_meta.json

## Common Edit Hotspots

- Backbone architecture edits belong here.
- Sampling strategy and loss experiments also belong here.
- Long-running performance issues usually need inspection here together with features.py.

## Top-Level Symbols

### `GraphPhaseContext`

- Kind: `class`
- Lines: `34-39`
- Role: Bundle one phase's feature store, graph cache, and labels so GNN training code can pass context as one object.
- How to use: Construct or load it once, then pass it downstream instead of repeatedly rebuilding the same context.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.

### `GraphModelConfig`

- Kind: `class`
- Lines: `43-154`
- Role: Serializable configuration object for sampling, loss, normalization, negative sampling, scheduler, and temporal sampling behavior.
- How to use: Read its fields or methods from the surrounding pipeline; this class is usually not invoked directly from the shell.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `to_dict(self) -> dict[str, Any]` lines `75-107`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Serialize the current object into a JSON-safe dict for checkpoints or summaries.
  - `from_dict(cls, payload: dict[str, Any] | None) -> 'GraphModelConfig'` lines `110-144`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Reconstruct the object from saved metadata when reloading a run.
  - `use_legacy_path(self) -> bool` lines `146-154`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Compatibility helper that tells the caller whether the experiment should fall back to older training logic.

### `SampledSubgraph`

- Kind: `class`
- Lines: `158-166`
- Role: Container holding the local-node list, sampled edges, relation ids, timestamps, and local target indices for one subgraph batch.
- How to use: Read its fields or methods from the surrounding pipeline; this class is usually not invoked directly from the shell.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.

### `TrainBatchStats`

- Kind: `class`
- Lines: `170-178`
- Role: Per-batch summary values used in training logs such as sampled subgraph size and positive rate.
- How to use: Read its fields or methods from the surrounding pipeline; this class is usually not invoked directly from the shell.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `positive_rate(self) -> float` lines `177-178`: Training helper that optimizes the current model on the project split.. Usage: Convenience property used in logging or monitoring to summarize how many positives are in the current batch.

### `_append_text_line(path: Path, line: str) -> None`

- Kind: `function`
- Lines: `181-185`
- Role: Append one human-readable log line to a training log file.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_append_jsonl(path: Path, payload: dict[str, Any]) -> None`

- Kind: `function`
- Lines: `188-192`
- Role: Append one JSON event line to a jsonl metrics file.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_write_history_csv(path: Path, rows: list[dict[str, Any]]) -> None`

- Kind: `function`
- Lines: `195-203`
- Role: Materialize the accumulated epoch history as a CSV file.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_plot_training_curves(path: Path, rows: list[dict[str, Any]]) -> str | None`

- Kind: `function`
- Lines: `206-260`
- Role: Render loss and metric curves from the stored epoch history.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_sample_edge_indices(edge_timestamp: np.ndarray, fanout: int, rng: np.random.Generator, snapshot_end: int | None, sampler: str = 'uniform', recent_window: int = 50, recent_ratio: float = 0.8, training: bool = True) -> np.ndarray`

- Kind: `function`
- Lines: `263-329`
- Role: Choose legal edge indices for one frontier node under fanout and optional temporal cutoff constraints.
- How to use: Use this to build a local sampled subset or subgraph instead of materializing the full graph structure.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `sample_relation_subgraph(graph: GraphCache, seed_nodes: np.ndarray, fanouts: list[int], rng: np.random.Generator, snapshot_end: int | None = None, sampler: str = 'uniform', recent_window: int = 50, recent_ratio: float = 0.8, training: bool = True) -> SampledSubgraph`

- Kind: `function`
- Lines: `332-464`
- Role: Sample a relation-aware local subgraph around one batch of seed nodes.
- How to use: Use this to build a local sampled subset or subgraph instead of materializing the full graph structure.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_sample_single_seed_subgraph(graph: GraphCache, seed: int, fanouts: list[int], rng: np.random.Generator, snapshot_end: int | None = None, sampler: str = 'uniform', recent_window: int = 50, recent_ratio: float = 0.8, training: bool = True) -> SampledSubgraph`

- Kind: `function`
- Lines: `467-585`
- Role: Fast path for single-seed meanmax pooling cases to reduce repeated list / dict construction.
- How to use: Use this to build a local sampled subset or subgraph instead of materializing the full graph structure.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `sample_batched_relation_subgraphs(graph: GraphCache, seed_nodes: np.ndarray, fanouts: list[int], rng: np.random.Generator, snapshot_end: int | None = None, sampler: str = 'uniform', recent_window: int = 50, recent_ratio: float = 0.8, training: bool = True) -> SampledSubgraph`

- Kind: `function`
- Lines: `588-657`
- Role: Sample multiple seed-node subgraphs together and pack them for batched processing.
- How to use: Use this to build a local sampled subset or subgraph instead of materializing the full graph structure.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `TimeEncoder`

- Kind: `class`
- Lines: `660-670`
- Role: Sinusoidal-like time encoding module used to inject edge-time information into temporal models.
- How to use: Read its fields or methods from the surrounding pipeline; this class is usually not invoked directly from the shell.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, out_dim: int) -> None` lines `661-667`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.
  - `forward(self, relative_time: torch.Tensor) -> torch.Tensor` lines `669-670`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: PyTorch forward pass used during training and inference; not a shell-facing entrypoint.

### `SafeBatchNorm1d`

- Kind: `class`
- Lines: `673-681`
- Role: BatchNorm wrapper that avoids pathological behavior on very small batches.
- How to use: Read its fields or methods from the surrounding pipeline; this class is usually not invoked directly from the shell.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, dim: int) -> None` lines `674-676`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.
  - `forward(self, x: torch.Tensor) -> torch.Tensor` lines `678-681`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: PyTorch forward pass used during training and inference; not a shell-facing entrypoint.

### `_make_norm(kind: str, dim: int) -> nn.Module`

- Kind: `function`
- Lines: `684-689`
- Role: Factory for layer norm, safe batch norm, or identity normalization.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_compute_grad_norm(parameters: Any) -> float`

- Kind: `function`
- Lines: `692-699`
- Role: Measure gradient norm for monitoring and optional clipping diagnostics.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_focal_bce_with_logits(logits: torch.Tensor, targets: torch.Tensor, pos_weight: torch.Tensor | None, gamma: float, alpha: float) -> torch.Tensor`

- Kind: `function`
- Lines: `702-722`
- Role: Compute the focal BCE variant used when focal loss is enabled.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_pairwise_ranking_loss(logits: torch.Tensor, targets: torch.Tensor, margin: float) -> torch.Tensor`

- Kind: `function`
- Lines: `725-735`
- Role: Compute the ranking term used when ranking-enhanced losses are enabled.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_dirichlet_energy(x: torch.Tensor, edge_src: torch.Tensor, edge_dst: torch.Tensor) -> torch.Tensor`

- Kind: `function`
- Lines: `738-746`
- Role: Compute a smoothness-style graph regularity diagnostic on embeddings.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_pool_mean_max(values: torch.Tensor, group_ids: torch.Tensor, num_groups: int) -> tuple[torch.Tensor, torch.Tensor]`

- Kind: `function`
- Lines: `749-789`
- Role: Build the mean/max pooled subgraph head input for target-node or subgraph fusion logic.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `_segment_softmax(scores: torch.Tensor, group_ids: torch.Tensor, num_groups: int) -> torch.Tensor`

- Kind: `function`
- Lines: `792-817`
- Role: Compute softmax values inside grouped edge segments for attention-style aggregation.
- How to use: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
- Side effects / outputs: Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence.

### `RelationSAGELayer`

- Kind: `class`
- Lines: `820-861`
- Role: Relation-aware SAGE message-passing layer used by the baseline GraphSAGE stack.
- How to use: Use it only as part of the PyTorch model stack; it is not a standalone CLI entrypoint.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, in_dim: int, out_dim: int, num_relations: int, rel_dim: int, time_dim: int = 0) -> None` lines `821-834`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.
  - `forward(self, x: torch.Tensor, edge_src: torch.Tensor, edge_dst: torch.Tensor, rel_ids: torch.Tensor, time_feature: torch.Tensor | None = None) -> torch.Tensor` lines `836-861`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: PyTorch forward pass used during training and inference; not a shell-facing entrypoint.

### `ModernRelationBlock`

- Kind: `class`
- Lines: `864-948`
- Role: Modernized relation block with residual / FFN / normalization options for temporal GraphSAGE variants.
- How to use: Use it only as part of the PyTorch model stack; it is not a standalone CLI entrypoint.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, hidden_dim: int, edge_dim: int, dropout: float, norm: str, residual: bool, ffn: bool, edge_encoder: str) -> None` lines `865-906`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.
  - `forward(self, x: torch.Tensor, edge_src: torch.Tensor, edge_dst: torch.Tensor, edge_emb: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]` lines `908-948`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: PyTorch forward pass used during training and inference; not a shell-facing entrypoint.

### `ModernRelationAttentionBlock`

- Kind: `class`
- Lines: `951-1033`
- Role: Attention-based relation block used by the temporal GAT variant.
- How to use: Use it only as part of the PyTorch model stack; it is not a standalone CLI entrypoint.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, hidden_dim: int, edge_dim: int, dropout: float, norm: str, residual: bool, ffn: bool, edge_encoder: str) -> None` lines `952-999`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.
  - `forward(self, x: torch.Tensor, edge_src: torch.Tensor, edge_dst: torch.Tensor, edge_emb: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]` lines `1001-1033`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: PyTorch forward pass used during training and inference; not a shell-facing entrypoint.

### `RelationGraphSAGENetwork`

- Kind: `class`
- Lines: `1036-1339`
- Role: Top-level neural network that stacks relation blocks and produces logits for target nodes.
- How to use: Use it only as part of the PyTorch model stack; it is not a standalone CLI entrypoint.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, input_dim: int, hidden_dim: int, num_layers: int, num_relations: int, rel_dim: int, dropout: float, temporal: bool, model_config: GraphModelConfig, aggregator_type: str = 'sage') -> None` lines `1037-1124`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.
  - `_build_edge_embedding(self, x: torch.Tensor, rel_ids: torch.Tensor, edge_relative_time: torch.Tensor | None) -> tuple[torch.Tensor | None, torch.Tensor | None]` lines `1126-1150`: Builder helper that assembles the next-stage object, feature block, or configuration bundle.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_subgraph_stats(self, node_repr: torch.Tensor, target_local_idx: torch.Tensor, node_subgraph_id: torch.Tensor, edge_subgraph_id: torch.Tensor, edge_dst: torch.Tensor, rel_ids: torch.Tensor, edge_relative_time: torch.Tensor | None) -> torch.Tensor` lines `1152-1211`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_forward_subgraph_head(self, node_repr: torch.Tensor, edge_repr: torch.Tensor, target_local_idx: torch.Tensor, node_subgraph_id: torch.Tensor | None, edge_subgraph_id: torch.Tensor | None, edge_dst: torch.Tensor, rel_ids: torch.Tensor, edge_relative_time: torch.Tensor | None) -> torch.Tensor` lines `1213-1266`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `forward(self, x: torch.Tensor, edge_src: torch.Tensor, edge_dst: torch.Tensor, rel_ids: torch.Tensor, edge_relative_time: torch.Tensor | None, target_local_idx: torch.Tensor, node_subgraph_id: torch.Tensor | None = None, edge_subgraph_id: torch.Tensor | None = None, return_details: bool = False) -> torch.Tensor | tuple[torch.Tensor, dict[str, float]]` lines `1268-1339`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: PyTorch forward pass used during training and inference; not a shell-facing entrypoint.

### `BaseGraphSAGEExperiment`

- Kind: `class`
- Lines: `1342-2495`
- Role: Main training / inference wrapper for graph models, including batch building, hard negatives, losses, logging, save/load, and evaluation.
- How to use: Instantiate it inside the training entrypoint, then call `fit(...)`, `predict_proba(...)`, and `save(...)` as needed.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, model_name: str, seed: int, input_dim: int, num_relations: int, max_day: int, feature_groups: list[str] | None = None, hidden_dim: int = 128, num_layers: int = 2, rel_dim: int = 32, fanouts: list[int] | None = None, batch_size: int = 1024, epochs: int = 4, learning_rate: float = 0.001, weight_decay: float = 1e-05, dropout: float = 0.2, device: str | None = None, temporal: bool = False, aggregator_type: str = 'sage', graph_config: GraphModelConfig | None = None, feature_normalizer_state: HybridFeatureNormalizerState | None = None) -> None` lines `1343-1399`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.
  - `_hard_negative_pool_key(self, snapshot_end: int | None) -> int` lines `1401-1402`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_hard_negative_enabled(self) -> bool` lines `1404-1408`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_uses_ranking_loss(self) -> bool` lines `1410-1411`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_iter_train_partitions(self, context: GraphPhaseContext, node_ids: np.ndarray) -> list[tuple[np.ndarray, np.ndarray, int | None]]` lines `1413-1432`: Training helper that optimizes the current model on the project split.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_compute_loss(self, logits: torch.Tensor, targets: torch.Tensor, pos_weight: torch.Tensor) -> tuple[torch.Tensor, dict[str, float]]` lines `1434-1469`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_current_hard_negative_pool_size(self) -> int` lines `1471-1472`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_current_hard_negative_candidate_count(self) -> int` lines `1474-1477`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_maybe_refresh_hard_negative_pools(self, context: GraphPhaseContext, train_ids: np.ndarray, epoch: int, rng: np.random.Generator) -> dict[str, int | bool]` lines `1479-1588`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_sample_negative_partition(self, neg_nodes: np.ndarray, neg_positions: np.ndarray, sampled_negatives: int, snapshot_end: int | None, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, int]` lines `1590-1711`: Sampling helper used to create local subgraphs, negatives, or reduced node subsets.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_iter_batches(self, context: GraphPhaseContext, node_ids: np.ndarray, training: bool, rng: np.random.Generator) -> list[tuple[np.ndarray, np.ndarray, int | None]]` lines `1713-1757`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_chunk_batch_partition(self, nodes: np.ndarray, positions: np.ndarray, snapshot_end: int | None, effective_batch_size: int) -> list[tuple[np.ndarray, np.ndarray, int | None]]` lines `1759-1773`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_build_balanced_partition_batches(self, nodes: np.ndarray, positions: np.ndarray, labels: np.ndarray, snapshot_end: int | None, rng: np.random.Generator, effective_batch_size: int) -> tuple[list[tuple[np.ndarray, np.ndarray, int | None]], TrainBatchStats]` lines `1775-1871`: Builder helper that assembles the next-stage object, feature block, or configuration bundle.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_build_train_batches(self, context: GraphPhaseContext, node_ids: np.ndarray, rng: np.random.Generator) -> tuple[list[tuple[np.ndarray, np.ndarray, int | None]], TrainBatchStats]` lines `1873-1931`: Builder helper that assembles the next-stage object, feature block, or configuration bundle.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_sample_batch_subgraph(self, graph: GraphCache, batch_nodes: np.ndarray, rng: np.random.Generator, snapshot_end: int | None, training: bool) -> SampledSubgraph` lines `1933-1957`: Sampling helper used to create local subgraphs, negatives, or reduced node subsets.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `_tensorize_subgraph(self, context: GraphPhaseContext, subgraph: SampledSubgraph, snapshot_end: int | None) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor | None, torch.Tensor, torch.Tensor | None, torch.Tensor | None]` lines `1959-2030`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice.
  - `fit(self, context: GraphPhaseContext, train_ids: np.ndarray, val_ids: np.ndarray, artifact_dir: Path | None = None) -> dict[str, float]` lines `2032-2344`: Run the full multi-epoch graph training loop, logging metrics and early-stopping on phase1 validation AUC.. Usage: Call after preparing features, node ids, and labels. This is the optimization stage that updates model parameters.
  - `predict_proba(self, context: GraphPhaseContext, node_ids: np.ndarray, batch_seed: int | None = None, progress_desc: str | None = None, show_progress: bool = True) -> np.ndarray` lines `2347-2417`: Run batched subgraph inference and return probabilities for the requested node ids.. Usage: Call on a fitted model to obtain fraud probabilities aligned to the requested node ids.
  - `save(self, run_dir: Path) -> None` lines `2419-2446`: Persist graph model weights and metadata.. Usage: Call after a successful fit so later comparison, blending, or deployment steps can reuse the trained artifact.
  - `load(cls, run_dir: Path, input_dim: int, num_relations: int, device: str | None = None) -> 'BaseGraphSAGEExperiment'` lines `2449-2495`: Restore a saved graph experiment from disk.. Usage: Call when you need to reopen a saved training artifact without retraining.

### `RelationGraphSAGEExperiment`

- Kind: `class`
- Lines: `2498-2502`
- Role: Concrete static relation GraphSAGE experiment wrapper.
- How to use: Instantiate it inside the training entrypoint, then call `fit(...)`, `predict_proba(...)`, and `save(...)` as needed.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, *args: Any, **kwargs: Any) -> None` lines `2499-2502`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.

### `TemporalRelationGraphSAGEExperiment`

- Kind: `class`
- Lines: `2505-2509`
- Role: Concrete temporal GraphSAGE experiment wrapper.
- How to use: Instantiate it inside the training entrypoint, then call `fit(...)`, `predict_proba(...)`, and `save(...)` as needed.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, *args: Any, **kwargs: Any) -> None` lines `2506-2509`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.

### `TemporalRelationGATExperiment`

- Kind: `class`
- Lines: `2512-2516`
- Role: Concrete temporal relation attention experiment wrapper.
- How to use: Instantiate it inside the training entrypoint, then call `fit(...)`, `predict_proba(...)`, and `save(...)` as needed.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, *args: Any, **kwargs: Any) -> None` lines `2513-2516`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.

