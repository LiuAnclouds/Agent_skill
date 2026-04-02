# Experiment Architecture

## End-To-End Data Flow

```text
raw phase1/phase2 npz
-> experiment/eda/data_loader.py
-> experiment/eda/analysis.py
-> recommended_split.json + EDA artifacts
-> experiment/training/features.py build_feature_artifacts
-> feature caches + graph caches
-> experiment/training/run_training.py or run_xgb_*.py
-> experiment/outputs/training/models/<family>/<run_name>/summary.json
```

## Model Families

- `m1_tabular` [baseline]: Raw node features plus missingness baseline.
- `m2_hybrid` [baseline]: Handcrafted structural, background, edge-type, and time features built in features.py.
- `m3_neighbor` [baseline]: m2_hybrid plus offline 1-hop neighbor aggregation blocks.
- `m4_graphsage` [gnn]: Relation-aware GraphSAGE baseline without explicit temporal encoding.
- `m5_temporal_graphsage` [gnn]: Time-aware relation GraphSAGE benchmark with modern training options.
- `m6_temporal_gat` [gnn]: Temporal relation attention backbone that replaces SAGE aggregation with attention-style message passing.
- `xgboost_gpu probes` [experimental]: Fast CUDA XGBoost exploration track for graph-propagation, relation-mean, and covariate-shift ideas.

## Model Family Detail

### `m1_tabular`

- Type: `baseline`
- Core idea: Raw node features plus missingness baseline.
- Typical inputs: Mostly raw phase feature columns with simple missingness support.
- Strengths: Fast, reproducible, and useful as the minimum baseline when graph ideas are not yet validated.
- Risks: Usually too weak to capture multi-hop or relation-specific fraud patterns on its own.
- When to use: Use for sanity checks, feature smoke tests, and the lower bound in ablation tables.

### `m2_hybrid`

- Type: `baseline`
- Core idea: Handcrafted structural, background, edge-type, and time features built in features.py.
- Typical inputs: Raw node features plus engineered structural and temporal statistics from the offline feature builder.
- Strengths: Captures substantial graph context without paying GNN training cost; strong baseline for fast iteration.
- Risks: Still limited by manual aggregation design and may miss finer temporal interaction patterns.
- When to use: Use when comparing handcrafted feature quality or before spending time on long neural runs.

### `m3_neighbor`

- Type: `baseline`
- Core idea: m2_hybrid plus offline 1-hop neighbor aggregation blocks.
- Typical inputs: m2 features plus cached neighbor aggregates from offline graph sweeps.
- Strengths: Usually stronger than pure tabular baselines while remaining much faster than online subgraph GNN training.
- Risks: Can become cache-heavy and still lacks adaptive message passing during training.
- When to use: Use as the main fast tabular benchmark and as the feature base for GPU XGBoost probes.

### `m4_graphsage`

- Type: `gnn`
- Core idea: Relation-aware GraphSAGE baseline without explicit temporal encoding.
- Typical inputs: Sampled local subgraphs with relation ids and node features, but weaker temporal conditioning than m5/m6.
- Strengths: Cleaner baseline for isolating the contribution of online graph message passing itself.
- Risks: May underfit the time-shifted validation regime because temporal structure is only weakly expressed.
- When to use: Use for backbone ablations or when testing whether temporal modules are actually helping.

### `m5_temporal_graphsage`

- Type: `gnn`
- Core idea: Time-aware relation GraphSAGE benchmark with modern training options.
- Typical inputs: Sampled temporal subgraphs, relation ids, time encodings, and engineered node features.
- Strengths: Current main temporal GraphSAGE benchmark and the most direct continuation of the existing codebase.
- Risks: Sampling cost is high, and stronger fitting does not automatically solve the severe time-shift generalization gap.
- When to use: Use when the experiment specifically targets sampling, losses, temporal encoding, or GraphSAGE-style backbone updates.

### `m6_temporal_gat`

- Type: `gnn`
- Core idea: Temporal relation attention backbone that replaces SAGE aggregation with attention-style message passing.
- Typical inputs: Same broad graph context as m5, but the backbone uses attention-based aggregation instead of plain SAGE aggregation.
- Strengths: Tests whether relation-aware attention is more expressive than the SAGE baseline under the same data regime.
- Risks: More expressive blocks can be slower and still fail if the bottleneck is feature/split mismatch rather than backbone capacity.
- When to use: Use for architecture upgrades when the user wants a more modern attention-flavored graph backbone.

### `xgboost_gpu probes`

- Type: `experimental`
- Core idea: Fast CUDA XGBoost exploration track for graph-propagation, relation-mean, and covariate-shift ideas.
- Typical inputs: Cached offline features, propagated blocks, relation-specific aggregates, or unsupervised weighting signals.
- Strengths: Very fast to iterate, cheap to ablate, and useful for deciding whether a hypothesis has signal before a long GNN run.
- Risks: Probe scripts can over-fragment the search space if they are not compared under a disciplined table.
- When to use: Use for quick signal checks, new feature ideas, or domain-shift probes that would be slow to test in a neural pipeline.

## Key Contracts

- `experiment/outputs/eda/recommended_split.json` defines the main evaluation split contract.
- `FeatureStore` and `GraphCache` are the stable runtime interfaces between offline build and training.
- `summary.json` is the stable comparison artifact for every meaningful experiment run.

## Artifact Layers

- Raw dataset layer: `experiment/dataset/phase*_gdata.npz`
- EDA layer: `experiment/outputs/eda/` tables, plots, markdown reports, and `recommended_split.json`
- Cache layer: `experiment/outputs/training/features/` memmaps, manifests, and graph arrays
- Training run layer: `experiment/outputs/training/models/<family>/<run_name>/`
- Skill memory layer: this skill's generated markdown bundle summarizing the live repository state

## Why This Architecture Exists

- The dataset is too large for repeated full recomputation during every run.
- Validation is deliberately time-shifted, so experiments need to be reproducible and leakage-safe.
- GNN experiments are slow, so faster GPU tabular probes are needed as a side track for hypothesis testing.
