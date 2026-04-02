from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_PROJECT_ROOT = Path("/home/moonxkj/Desktop/MyWork/Graduation_Project")
DEFAULT_SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "graduation-project-dgraph-mentor"

LABEL_NAME_MAP = {
    -100: "test_holdout",
    0: "normal",
    1: "fraud",
    2: "background_2",
    3: "background_3",
}

TOP_LEVEL_NOTES = {
    "article": "Research-paper PDFs, reading notes, Feishu exports, and literature support material. Useful for method inspiration, not as executable benchmark truth.",
    "article_code": "Reference implementations copied from papers or external repos for study, comparison, or selective reuse ideas.",
    "data": "Auxiliary local data assets outside the main experiment dataset layout if present.",
    "example": "Small examples or scratch assets used for demonstration rather than core experiments.",
    "experiment": "The thesis core: EDA, feature building, training entrypoints, model code, and saved outputs.",
    "other": "Miscellaneous utilities or archived material that is not on the main benchmark path.",
    ".git": "Git metadata; not part of the modeling pipeline itself.",
}

IGNORED_TOP_LEVEL_DIRS = {
    ".claude",
    ".codex_tmp_skill",
    ".git",
    ".idea",
    "__pycache__",
    "catboost_info",
}

FILE_PURPOSES = {
    "experiment/eda/data_loader.py": "Resolve the XinYe dataset paths, flatten arrays, validate schema assumptions, and load one phase into a typed PhaseData container.",
    "experiment/eda/analysis.py": "Run the reproducible EDA stack: overview, feature profile, graph statistics, temporal behavior, drift checks, and the recommended time-aware split.",
    "experiment/eda/run_eda.py": "CLI entrypoint for the EDA pipeline.",
    "experiment/training/common.py": "Shared training utilities for paths, metrics, split loading, seeding, prediction saving, and device resolution.",
    "experiment/training/features.py": "Offline feature-cache and graph-cache builder plus runtime FeatureStore and GraphCache readers.",
    "experiment/training/gbdt_models.py": "LightGBM baseline wrapper used by the unified training CLI.",
    "experiment/training/gnn_models.py": "Graph sampling, relation-aware message passing layers, temporal encoders, training loop, logging, hard-negative mining, and GNN inference wrappers.",
    "experiment/training/run_training.py": "Unified CLI for build_features, LightGBM / GNN training, and prediction blending.",
    "experiment/training/run_xgb_graphprop.py": "GPU XGBoost exploration script for propagated graph features such as A*X and A^2*X style blocks.",
    "experiment/training/run_xgb_relmean.py": "GPU XGBoost exploration script for relation-specific neighbor mean features.",
    "experiment/training/run_xgb_covshift.py": "GPU XGBoost exploration script for covariate-shift weighting between time-split train and val distributions.",
}

SYMBOL_OVERRIDES = {
    "experiment/eda/data_loader.py": {
        "PhaseData": "Immutable in-memory bundle for one dataset phase, including node features, labels, edges, timestamps, and official train/test node ids.",
        "resolve_dataset_path": "Find the canonical npz file for a named phase under the current dataset layout.",
        "_flatten_array": "Flatten label or mask arrays to one dimension and optionally cast dtype.",
        "_validate_phase_data": "Assert that the loaded phase matches the expected DGraph schema and label assumptions.",
        "load_phase": "Load one dataset phase from disk and return a validated PhaseData object.",
    },
    "experiment/eda/run_eda.py": {
        "parse_args": "Parse CLI flags for phase selection, analysis modules, and output directory.",
        "main": "Entrypoint that expands phase selection and launches run_eda().",
    },
    "experiment/eda/analysis.py": {
        "configure_matplotlib": "Set a font stack that can render Chinese labels in generated plots and keep minus signs readable.",
        "ensure_dir": "Create an artifact directory if missing and return the same path for chained writes.",
        "write_csv": "Write a list of dict rows into a UTF-8 CSV artifact with stable field ordering.",
        "write_json": "Persist a JSON summary artifact for later reuse by training or reporting code.",
        "write_square_csv": "Write a square matrix such as a correlation or PSI-style table with row and column headers.",
        "label_name": "Map numeric dataset labels to readable names like normal, fraud, and background classes.",
        "quantile_row": "Convert one numeric vector into a prefixed quantile-stat dict row for CSV summaries.",
        "basic_stats": "Return a compact statistics dict used inside EDA summaries.",
        "sample_values": "Downsample large vectors for plotting so EDA remains tractable on million-scale data.",
        "plot_empirical_cdf": "Draw an empirical CDF curve on an existing matplotlib axis.",
        "build_time_windows": "Split a time-like vector into quantile-based windows for later temporal summaries.",
        "build_phase_output_dir": "Create the output subdirectory for a specific phase under the EDA output root.",
        "get_train_target": "Return the official supervised node ids and labels for one dataset phase.",
        "analyze_overview": "Produce the high-level size, label, edge-type, and train/test distribution summary for one phase.",
        "analyze_features": "Profile raw feature distributions, missingness, normal-vs-fraud gaps, and per-group missing patterns.",
        "compute_degree_arrays": "Compute indegree, outdegree, and total degree arrays from the raw edge list.",
        "compute_temporal_core": "Compute first_active, last_active, and active_span arrays used throughout EDA and feature building.",
        "analyze_graph": "Profile graph structure, background-node effects, degree patterns, and edge-type behavior.",
        "analyze_temporal": "Profile node activity over time, time windows, and train-class temporal behavior.",
        "_psi": "Compute a population stability style drift score between reference and current distributions.",
        "_build_drift_bins": "Create quantile-based bins for drift calculations.",
        "analyze_drift": "Compare phase1 and phase2 feature drift and write a drift summary report.",
        "build_recommended_split": "Create the project's leakage-safe time-aware phase1 train/val split and phase2 external evaluation ids.",
        "run_eda": "Execute the requested EDA stages, aggregate summaries, and persist the full artifact bundle.",
    },
    "experiment/training/common.py": {
        "ExperimentSplit": "Container for the recommended phase1 train/val ids plus the phase2 external evaluation ids.",
        "compute_binary_classification_metrics": "Compute ROC-AUC, AP, and PR-AUC for binary fraud detection outputs.",
        "load_experiment_split": "Load the persisted time-aware split built during EDA.",
        "load_phase_arrays": "Read selected arrays such as y/train_mask/test_mask directly from a phase npz file.",
        "slice_node_ids": "Optional random subsampling helper for smoke tests or reduced-size runs.",
        "save_prediction_npz": "Persist node ids, labels, and probabilities into a compact npz artifact.",
        "resolve_device": "Choose the requested torch device or default to CUDA when available.",
    },
    "experiment/training/features.py": {
        "GraphCache": "Runtime bundle of CSR-like in/out adjacency arrays, edge metadata, and time-bucket annotations.",
        "HybridFeatureNormalizerState": "Serializable description of how hybrid feature normalization should be applied at training and inference time.",
        "FeatureStore": "Memmap-backed feature reader that assembles selected feature groups by node id.",
        "build_hybrid_feature_normalizer": "Fit the hybrid normalization statistics from the phase1 train split only.",
        "_build_neighbor_features": "Construct the offline 1-hop neighbor aggregation blocks used by the m3 neighbor feature set.",
        "build_phase_feature_artifacts": "Core offline build path for one phase: core features, optional neighbor features, graph cache, and manifest.",
        "build_feature_artifacts": "Multi-phase wrapper around build_phase_feature_artifacts().",
        "load_feature_manifest": "Read feature_manifest.json for one phase.",
        "load_graph_cache": "Open the graph cache arrays for one phase as memmaps.",
        "default_feature_groups": "Map each model family name to its default feature-group recipe.",
    },
    "experiment/training/gbdt_models.py": {
        "LightGBMExperiment": "Wrapper around a LightGBM fraud classifier with fit/predict/save/load helpers aligned to this project.",
        "LightGBMExperiment.fit": "Train the LightGBM baseline on the phase1 train split and early-stop on phase1 val AUC.",
        "LightGBMExperiment.predict_proba": "Return fraud probabilities for a node-id slice.",
        "LightGBMExperiment.save": "Persist the fitted booster and feature-importance metadata.",
        "LightGBMExperiment.load": "Restore a saved LightGBM experiment from disk.",
    },
    "experiment/training/gnn_models.py": {
        "GraphPhaseContext": "Bundle one phase's feature store, graph cache, and labels so GNN training code can pass context as one object.",
        "GraphModelConfig": "Serializable configuration object for sampling, loss, normalization, negative sampling, scheduler, and temporal sampling behavior.",
        "SampledSubgraph": "Container holding the local-node list, sampled edges, relation ids, timestamps, and local target indices for one subgraph batch.",
        "TrainBatchStats": "Per-batch summary values used in training logs such as sampled subgraph size and positive rate.",
        "_append_text_line": "Append one human-readable log line to a training log file.",
        "_append_jsonl": "Append one JSON event line to a jsonl metrics file.",
        "_write_history_csv": "Materialize the accumulated epoch history as a CSV file.",
        "_plot_training_curves": "Render loss and metric curves from the stored epoch history.",
        "_sample_edge_indices": "Choose legal edge indices for one frontier node under fanout and optional temporal cutoff constraints.",
        "sample_relation_subgraph": "Sample a relation-aware local subgraph around one batch of seed nodes.",
        "_sample_single_seed_subgraph": "Fast path for single-seed meanmax pooling cases to reduce repeated list / dict construction.",
        "sample_batched_relation_subgraphs": "Sample multiple seed-node subgraphs together and pack them for batched processing.",
        "TimeEncoder": "Sinusoidal-like time encoding module used to inject edge-time information into temporal models.",
        "SafeBatchNorm1d": "BatchNorm wrapper that avoids pathological behavior on very small batches.",
        "_make_norm": "Factory for layer norm, safe batch norm, or identity normalization.",
        "_compute_grad_norm": "Measure gradient norm for monitoring and optional clipping diagnostics.",
        "_focal_bce_with_logits": "Compute the focal BCE variant used when focal loss is enabled.",
        "_pairwise_ranking_loss": "Compute the ranking term used when ranking-enhanced losses are enabled.",
        "_dirichlet_energy": "Compute a smoothness-style graph regularity diagnostic on embeddings.",
        "_pool_mean_max": "Build the mean/max pooled subgraph head input for target-node or subgraph fusion logic.",
        "_segment_softmax": "Compute softmax values inside grouped edge segments for attention-style aggregation.",
        "RelationSAGELayer": "Relation-aware SAGE message-passing layer used by the baseline GraphSAGE stack.",
        "ModernRelationBlock": "Modernized relation block with residual / FFN / normalization options for temporal GraphSAGE variants.",
        "ModernRelationAttentionBlock": "Attention-based relation block used by the temporal GAT variant.",
        "RelationGraphSAGENetwork": "Top-level neural network that stacks relation blocks and produces logits for target nodes.",
        "BaseGraphSAGEExperiment": "Main training / inference wrapper for graph models, including batch building, hard negatives, losses, logging, save/load, and evaluation.",
        "BaseGraphSAGEExperiment.fit": "Run the full multi-epoch graph training loop, logging metrics and early-stopping on phase1 validation AUC.",
        "BaseGraphSAGEExperiment.predict_proba": "Run batched subgraph inference and return probabilities for the requested node ids.",
        "BaseGraphSAGEExperiment.save": "Persist graph model weights and metadata.",
        "BaseGraphSAGEExperiment.load": "Restore a saved graph experiment from disk.",
        "RelationGraphSAGEExperiment": "Concrete static relation GraphSAGE experiment wrapper.",
        "TemporalRelationGraphSAGEExperiment": "Concrete temporal GraphSAGE experiment wrapper.",
        "TemporalRelationGATExperiment": "Concrete temporal relation attention experiment wrapper.",
    },
    "experiment/training/run_training.py": {
        "parse_args": "Parse the unified CLI for feature building, tabular/GNN training, and blending.",
        "run_build_features": "Launch the offline feature and graph-cache build.",
        "run_train_lightgbm": "Train tabular baselines on the recommended split and write per-seed plus averaged predictions.",
        "_make_graph_contexts": "Open feature stores, graph caches, and labels for both phases.",
        "run_train_graph": "Train GNN models, evaluate on phase1 val and phase2 external, and write logs / curves / summaries.",
        "run_blend": "Blend multiple saved model runs through logistic stacking on validation logits.",
        "main": "Top-level dispatcher for the unified training CLI.",
    },
    "experiment/training/run_xgb_graphprop.py": {
        "main": "Build propagated graph-feature blocks, train CUDA XGBoost, and save the resulting leaderboard artifact.",
    },
    "experiment/training/run_xgb_relmean.py": {
        "main": "Build relation-specific neighbor mean features, train CUDA XGBoost, and save the resulting leaderboard artifact.",
    },
    "experiment/training/run_xgb_covshift.py": {
        "main": "Train a domain classifier between train and val, derive sample weights, and train a weighted CUDA XGBoost fraud model.",
    },
}

DEFAULT_RECENT_CHANGES = [
    {
        "timestamp": "2026-04-01T18:17:51+08:00",
        "title": "Added GPU XGBoost covariate-shift probe",
        "summary": "Introduced run_xgb_covshift.py to test whether weighting phase1 train samples toward the later validation distribution can improve time-split generalization. The first smoke run reached domain_auc=1.0000 but val_auc only about 0.7665.",
        "paths": [
            "experiment/training/run_xgb_covshift.py",
            "experiment/outputs/training/models/xgboost_gpu/smoke_covshift_m3_v1/summary.json",
        ],
    },
    {
        "timestamp": "2026-04-01T18:15:49+08:00",
        "title": "Added GPU XGBoost relation-mean probe",
        "summary": "Introduced run_xgb_relmean.py to test relation-specific neighbor mean features by edge type. The first smoke run underperformed with val_auc about 0.7542, which suggests naive per-relation averaging is too noisy.",
        "paths": [
            "experiment/training/run_xgb_relmean.py",
            "experiment/outputs/training/models/xgboost_gpu/smoke_relmean_m3_alltypes_rawmiss_v1/summary.json",
        ],
    },
    {
        "timestamp": "2026-04-01T18:10:24+08:00",
        "title": "Added GPU XGBoost graph-propagation probe",
        "summary": "Introduced run_xgb_graphprop.py to test propagated feature blocks such as in1/out1/in2/out2 over m2 or m3 features. The full graphprop run reached val_auc about 0.78925, slightly above the plain m3 XGBoost baseline but still far below the 0.82 target.",
        "paths": [
            "experiment/training/run_xgb_graphprop.py",
            "experiment/outputs/training/models/xgboost_gpu/full_graphprop_m3m2_inout12_v1/summary.json",
        ],
    },
    {
        "timestamp": "2026-03-31T20:00:00+08:00",
        "title": "Expanded GNN training observability",
        "summary": "The unified training path now records PR-AUC and AP alongside ROC-AUC, writes per-seed logs and epoch metrics, and saves training curves so long GNN runs are easier to diagnose.",
        "paths": [
            "experiment/training/run_training.py",
            "experiment/training/gnn_models.py",
            "experiment/training/common.py",
        ],
    },
    {
        "timestamp": "2026-03-31T19:00:00+08:00",
        "title": "Expanded GNN optimization controls",
        "summary": "The graph training stack now includes balanced negative sampling, hard-negative mining, focal and ranking loss options, temporal sampler choices, and tqdm progress bars to support faster ablations.",
        "paths": [
            "experiment/training/run_training.py",
            "experiment/training/gnn_models.py",
        ],
    },
]

GOAL_NOTES = [
    "Primary internal target: push phase1_val_auc to at least 0.82 without any data leakage.",
    "Keep phase2_external_auc as the robustness check; improving val while collapsing external generalization is not acceptable.",
    "Use GPU in the Graph conda environment for heavy experiments. The user explicitly requested GPU rather than CPU training.",
    "Current evidence suggests the hard temporal split is the main bottleneck: phase1 train nodes are much earlier than phase1 val nodes, so distribution shift is severe.",
]

OPEN_DIRECTIONS = [
    "Improve time-aware sampling or time-conditioned feature engineering without leaking future information.",
    "Strengthen relation-aware modeling instead of global averaging. The current simple relation-mean probe was too weak, but more selective relation features remain open.",
    "Keep exploring GPU tabular models and graph-tabular hybrids because they are faster to iterate than long GNN runs.",
    "Revisit backbone updates such as stronger temporal GAT / Transformer-style modules once a faster feature or sampling baseline is stable.",
    "Consider calibrated ensembling or stacking only after a clearly stronger single-run validation model appears.",
    "Prepare the data-loading layer for future additional datasets; the current repository still assumes only the XinYe DGraph phase1/phase2 layout.",
]

FILE_GUIDE_NOTES = {
    "experiment/eda/analysis.py": {
        "when_to_read": "Read this file when you need to understand where the recommended train/val split comes from, why the current validation regime is time-aware, or how the generated EDA artifacts are produced.",
        "upstream": ["experiment/eda/run_eda.py"],
        "downstream": [
            "experiment/outputs/eda/*.json / *.csv / *.md",
            "experiment/training/common.py::load_experiment_split",
            "experiment/training/features.py temporal feature construction",
        ],
        "outputs": [
            "dataset_summary.json",
            "feature_profile.csv",
            "graph_profile.csv",
            "temporal_profile.csv",
            "drift_summary.md",
            "recommended_split.json",
        ],
        "change_points": [
            "Modify split strategy here if the project changes its validation philosophy.",
            "Adjust temporal windows, drift metrics, or artifact set here when EDA requirements expand.",
        ],
    },
    "experiment/eda/data_loader.py": {
        "when_to_read": "Read this file first when dataset paths change or when the repository needs to support more datasets.",
        "upstream": [],
        "downstream": [
            "experiment/eda/analysis.py",
            "experiment/training/features.py",
            "experiment/training/common.py",
        ],
        "outputs": ["Validated PhaseData objects in memory"],
        "change_points": [
            "Add new dataset filename conventions here.",
            "Relax or extend schema validation here if later datasets differ from XinYe DGraph.",
        ],
    },
    "experiment/eda/run_eda.py": {
        "when_to_read": "Read this file when you need the exact EDA CLI surface or want to add a new user-facing EDA command-line option.",
        "upstream": ["shell / terminal"],
        "downstream": ["experiment/eda/analysis.py"],
        "outputs": ["EDA run entrypoint only; artifacts are written by analysis.py"],
        "change_points": ["Expose new analysis stages or flags here after analysis.py changes."],
    },
    "experiment/training/common.py": {
        "when_to_read": "Read this file when a training change needs new shared metrics, new split loading, or reusable IO helpers.",
        "upstream": [
            "experiment/training/run_training.py",
            "experiment/training/gbdt_models.py",
            "experiment/training/gnn_models.py",
            "experiment/training/run_xgb_*.py",
        ],
        "downstream": ["All training summaries, predictions, and metric calculations"],
        "outputs": ["Metric dicts, split bundles, prediction npz files"],
        "change_points": [
            "Add new evaluation metrics here if all training flows should report them.",
            "Do not silently change load_experiment_split unless the evaluation contract changes everywhere.",
        ],
    },
    "experiment/training/features.py": {
        "when_to_read": "Read this file before touching model input features, feature normalization, graph cache layout, or any offline build logic.",
        "upstream": [
            "experiment/training/run_training.py build_features",
            "experiment/training/run_xgb_graphprop.py",
            "experiment/training/run_xgb_relmean.py",
            "experiment/training/run_xgb_covshift.py",
        ],
        "downstream": [
            "FeatureStore consumers in gbdt_models.py and gnn_models.py",
            "experiment/outputs/training/features/",
        ],
        "outputs": [
            "core_features.npy",
            "neighbor_features.npy",
            "feature_manifest.json",
            "graph/*.npy",
        ],
        "change_points": [
            "Add or remove feature groups here.",
            "If you change cache layout, update every reader that depends on FeatureStore or GraphCache.",
        ],
    },
    "experiment/training/gbdt_models.py": {
        "when_to_read": "Read this file when changing the LightGBM baseline behavior inside the unified training CLI.",
        "upstream": ["experiment/training/run_training.py::run_train_lightgbm"],
        "downstream": ["Saved LightGBM boosters and feature importance artifacts"],
        "outputs": ["model.txt", "model_meta.json", "feature_importance.csv"],
        "change_points": [
            "Tune baseline tabular behavior here if LightGBM remains part of the benchmark contract.",
        ],
    },
    "experiment/training/gnn_models.py": {
        "when_to_read": "Read this file when changing graph sampling, temporal handling, losses, hard negatives, the GNN backbone, logging, or inference behavior.",
        "upstream": ["experiment/training/run_training.py::run_train_graph"],
        "downstream": [
            "Per-seed GNN artifacts under experiment/outputs/training/models/",
            "phase1 val and phase2 external probabilities",
        ],
        "outputs": [
            "train.log",
            "epoch_metrics.csv / .jsonl",
            "training_curves.png",
            "model_meta.json",
        ],
        "change_points": [
            "Backbone architecture edits belong here.",
            "Sampling strategy and loss experiments also belong here.",
            "Long-running performance issues usually need inspection here together with features.py.",
        ],
    },
    "experiment/training/run_training.py": {
        "when_to_read": "Read this file when the user-facing training CLI changes, when a new model family is added to the main benchmark path, or when summary outputs need to change consistently.",
        "upstream": ["shell / terminal"],
        "downstream": [
            "experiment/training/features.py",
            "experiment/training/gbdt_models.py",
            "experiment/training/gnn_models.py",
            "experiment/outputs/training/models/",
        ],
        "outputs": ["Unified build/train/blend command surface and summary.json files"],
        "change_points": [
            "Add CLI flags here for new model families or new training options.",
            "Keep summary structure stable if downstream comparison scripts depend on it.",
        ],
    },
    "experiment/training/run_xgb_graphprop.py": {
        "when_to_read": "Read this file when exploring graph-propagated tabular feature blocks with CUDA XGBoost.",
        "upstream": ["shell / terminal"],
        "downstream": ["xgboost_gpu/<run_name>/ summary and predictions"],
        "outputs": ["summary.json", "phase1_val_predictions.npz", "phase2_external_predictions.npz"],
        "change_points": ["Graph-propagation feature recipes and caching strategy live here."],
    },
    "experiment/training/run_xgb_relmean.py": {
        "when_to_read": "Read this file when exploring relation-specific neighbor mean features with CUDA XGBoost.",
        "upstream": ["shell / terminal"],
        "downstream": ["xgboost_gpu/<run_name>/ summary and predictions"],
        "outputs": ["summary.json", "feature_importance.csv", "prediction npz files"],
        "change_points": ["Per-edge-type aggregation logic and cache layout live here."],
    },
    "experiment/training/run_xgb_covshift.py": {
        "when_to_read": "Read this file when testing unsupervised covariate-shift weighting between phase1 train and val.",
        "upstream": ["shell / terminal"],
        "downstream": ["xgboost_gpu/<run_name>/ summary and predictions"],
        "outputs": ["domain_model.json", "model.json", "prediction npz files"],
        "change_points": ["Domain classifier design and sample-weighting logic live here."],
    },
}

MODEL_FAMILY_NOTES = [
    {
        "name": "m1_tabular",
        "type": "baseline",
        "summary": "Raw node features plus missingness baseline.",
        "typical_inputs": "Mostly raw phase feature columns with simple missingness support.",
        "strengths": "Fast, reproducible, and useful as the minimum baseline when graph ideas are not yet validated.",
        "risks": "Usually too weak to capture multi-hop or relation-specific fraud patterns on its own.",
        "when_to_use": "Use for sanity checks, feature smoke tests, and the lower bound in ablation tables.",
    },
    {
        "name": "m2_hybrid",
        "type": "baseline",
        "summary": "Handcrafted structural, background, edge-type, and time features built in features.py.",
        "typical_inputs": "Raw node features plus engineered structural and temporal statistics from the offline feature builder.",
        "strengths": "Captures substantial graph context without paying GNN training cost; strong baseline for fast iteration.",
        "risks": "Still limited by manual aggregation design and may miss finer temporal interaction patterns.",
        "when_to_use": "Use when comparing handcrafted feature quality or before spending time on long neural runs.",
    },
    {
        "name": "m3_neighbor",
        "type": "baseline",
        "summary": "m2_hybrid plus offline 1-hop neighbor aggregation blocks.",
        "typical_inputs": "m2 features plus cached neighbor aggregates from offline graph sweeps.",
        "strengths": "Usually stronger than pure tabular baselines while remaining much faster than online subgraph GNN training.",
        "risks": "Can become cache-heavy and still lacks adaptive message passing during training.",
        "when_to_use": "Use as the main fast tabular benchmark and as the feature base for GPU XGBoost probes.",
    },
    {
        "name": "m4_graphsage",
        "type": "gnn",
        "summary": "Relation-aware GraphSAGE baseline without explicit temporal encoding.",
        "typical_inputs": "Sampled local subgraphs with relation ids and node features, but weaker temporal conditioning than m5/m6.",
        "strengths": "Cleaner baseline for isolating the contribution of online graph message passing itself.",
        "risks": "May underfit the time-shifted validation regime because temporal structure is only weakly expressed.",
        "when_to_use": "Use for backbone ablations or when testing whether temporal modules are actually helping.",
    },
    {
        "name": "m5_temporal_graphsage",
        "type": "gnn",
        "summary": "Time-aware relation GraphSAGE benchmark with modern training options.",
        "typical_inputs": "Sampled temporal subgraphs, relation ids, time encodings, and engineered node features.",
        "strengths": "Current main temporal GraphSAGE benchmark and the most direct continuation of the existing codebase.",
        "risks": "Sampling cost is high, and stronger fitting does not automatically solve the severe time-shift generalization gap.",
        "when_to_use": "Use when the experiment specifically targets sampling, losses, temporal encoding, or GraphSAGE-style backbone updates.",
    },
    {
        "name": "m6_temporal_gat",
        "type": "gnn",
        "summary": "Temporal relation attention backbone that replaces SAGE aggregation with attention-style message passing.",
        "typical_inputs": "Same broad graph context as m5, but the backbone uses attention-based aggregation instead of plain SAGE aggregation.",
        "strengths": "Tests whether relation-aware attention is more expressive than the SAGE baseline under the same data regime.",
        "risks": "More expressive blocks can be slower and still fail if the bottleneck is feature/split mismatch rather than backbone capacity.",
        "when_to_use": "Use for architecture upgrades when the user wants a more modern attention-flavored graph backbone.",
    },
    {
        "name": "xgboost_gpu probes",
        "type": "experimental",
        "summary": "Fast CUDA XGBoost exploration track for graph-propagation, relation-mean, and covariate-shift ideas.",
        "typical_inputs": "Cached offline features, propagated blocks, relation-specific aggregates, or unsupervised weighting signals.",
        "strengths": "Very fast to iterate, cheap to ablate, and useful for deciding whether a hypothesis has signal before a long GNN run.",
        "risks": "Probe scripts can over-fragment the search space if they are not compared under a disciplined table.",
        "when_to_use": "Use for quick signal checks, new feature ideas, or domain-shift probes that would be slow to test in a neural pipeline.",
    },
]


@dataclass
class SymbolDoc:
    kind: str
    name: str
    signature: str
    start_line: int
    end_line: int
    description: str
    methods: list["SymbolDoc"] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync the Graduation_Project skill references from the live project repository.",
    )
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT_ROOT)
    parser.add_argument("--skill-root", type=Path, default=DEFAULT_SKILL_ROOT)
    parser.add_argument("--record-change", default=None, help="Optional short summary of a new milestone change to append to recent memory.")
    parser.add_argument("--record-last-commit", action="store_true", help="Append the latest git commit subject and changed files to recent memory.")
    parser.add_argument("--install-hook", action="store_true", help="Install local post-commit and post-merge hooks in the project repository.")
    parser.add_argument("--mirror-installed-copy", action="store_true", help="After syncing the repository copy, also refresh ~/.codex/skills/<skill-name>.")
    parser.add_argument("--watch", action="store_true", help="Continuously watch for project changes and refresh the reference bundle.")
    parser.add_argument("--interval", type=float, default=20.0, help="Polling interval in seconds for --watch mode.")
    return parser.parse_args()


def run_command(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd is not None else None,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def safe_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_signature(node: ast.AST) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        parts: list[str] = []
        args = node.args
        positional = list(args.posonlyargs) + list(args.args)
        defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
        for arg, default in zip(positional, defaults, strict=True):
            piece = arg.arg
            if arg.annotation is not None:
                piece += f": {ast.unparse(arg.annotation)}"
            if default is not None:
                piece += f" = {ast.unparse(default)}"
            parts.append(piece)
        if args.vararg is not None:
            piece = f"*{args.vararg.arg}"
            if args.vararg.annotation is not None:
                piece += f": {ast.unparse(args.vararg.annotation)}"
            parts.append(piece)
        elif args.kwonlyargs:
            parts.append("*")
        for kw_arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
            piece = kw_arg.arg
            if kw_arg.annotation is not None:
                piece += f": {ast.unparse(kw_arg.annotation)}"
            if default is not None:
                piece += f" = {ast.unparse(default)}"
            parts.append(piece)
        if args.kwarg is not None:
            piece = f"**{args.kwarg.arg}"
            if args.kwarg.annotation is not None:
                piece += f": {ast.unparse(args.kwarg.annotation)}"
            parts.append(piece)
        rendered = ", ".join(parts)
        suffix = ""
        if node.returns is not None:
            suffix = f" -> {ast.unparse(node.returns)}"
        return f"{node.name}({rendered}){suffix}"
    if isinstance(node, ast.ClassDef):
        return node.name
    return getattr(node, "name", "<unknown>")


def heuristic_description(file_rel: str, symbol_name: str, kind: str) -> str:
    override = SYMBOL_OVERRIDES.get(file_rel, {}).get(symbol_name)
    if override:
        return override
    lowered = symbol_name.lower()
    if kind == "class":
        if lowered.endswith("experiment"):
            return "Experiment wrapper that holds configuration plus fit / predict / save lifecycle helpers."
        if lowered.endswith("context"):
            return "Data container that groups runtime context required by later pipeline stages."
        if lowered.endswith("cache"):
            return "Cache container that exposes precomputed arrays needed during training or EDA."
        if lowered.endswith("network") or lowered.endswith("layer") or lowered.endswith("block"):
            return "Neural-network building block used inside the graph model stack."
        return "Structured class in the experiment pipeline; inspect the listed methods for its concrete role."
    if "parse_args" in lowered:
        return "CLI argument parser for this module."
    if lowered == "main":
        return "Module entrypoint that orchestrates the main workflow."
    if "load" in lowered:
        return "Load helper that restores data, configuration, or saved artifacts from disk."
    if "save" in lowered or "write" in lowered:
        return "Artifact-writing helper used to persist outputs for later reuse."
    if "build" in lowered or "make" in lowered:
        return "Builder helper that assembles the next-stage object, feature block, or configuration bundle."
    if "sample" in lowered:
        return "Sampling helper used to create local subgraphs, negatives, or reduced node subsets."
    if "predict" in lowered:
        return "Inference helper that converts a fitted model into fraud probabilities or scores."
    if "fit" in lowered or "train" in lowered:
        return "Training helper that optimizes the current model on the project split."
    if "metric" in lowered or "auc" in lowered or "precision" in lowered:
        return "Metric helper used to evaluate fraud-detection predictions."
    if lowered.startswith("_"):
        return "Private helper used internally by this module; read together with its callers."
    return "Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline."


def heuristic_usage(file_rel: str, symbol_name: str, kind: str) -> str:
    note = FILE_GUIDE_NOTES.get(file_rel, {})
    lowered = symbol_name.lower()
    if kind == "class":
        if lowered.endswith("experiment"):
            return "Instantiate it inside the training entrypoint, then call `fit(...)`, `predict_proba(...)`, and `save(...)` as needed."
        if lowered.endswith("layer") or lowered.endswith("block") or lowered.endswith("network"):
            return "Use it only as part of the PyTorch model stack; it is not a standalone CLI entrypoint."
        if lowered.endswith("cache") or lowered.endswith("context"):
            return "Construct or load it once, then pass it downstream instead of repeatedly rebuilding the same context."
        return "Read its fields or methods from the surrounding pipeline; this class is usually not invoked directly from the shell."
    if lowered == "main":
        return "Run this through the file's CLI command; `main()` is the terminal-facing orchestration entrypoint."
    if lowered == "parse_args":
        return "Called automatically by `main()` to define the user-facing CLI contract."
    if lowered.startswith("run_"):
        return "This is a stage-level orchestrator. Prefer calling it indirectly through the module CLI unless you are importing the pipeline programmatically."
    if lowered.startswith("analyze_"):
        return "Call this from the EDA pipeline when you want one analysis block plus its artifact writes and summary payload."
    if lowered.startswith("build_"):
        return "Use this when you need to construct the next artifact bundle or derived object before training or reporting."
    if lowered.startswith("_build_"):
        return "Internal builder used by the parent public function; modify it when changing how that artifact is assembled."
    if lowered.startswith("load_") or lowered.startswith("_load_"):
        return "Use this to restore cached arrays, saved predictions, or configuration from disk."
    if lowered.startswith("save_") or lowered.startswith("_save_") or lowered.startswith("write_"):
        return "Use this to persist artifacts so later stages can reuse them without recomputation."
    if lowered.startswith("compute_") or lowered.startswith("safe_"):
        return "Call this when you need a deterministic derived statistic or robust evaluation metric."
    if lowered.startswith("sample_") or lowered.startswith("_sample_"):
        return "Use this to build a local sampled subset or subgraph instead of materializing the full graph structure."
    if lowered == "fit" or lowered.endswith(".fit"):
        return "Call after preparing features, node ids, and labels. This is the optimization stage that updates model parameters."
    if lowered == "predict_proba" or lowered.endswith(".predict_proba"):
        return "Call on a fitted model to obtain fraud probabilities aligned to the requested node ids."
    if lowered == "save" or lowered.endswith(".save"):
        return "Call after a successful fit so later comparison, blending, or deployment steps can reuse the trained artifact."
    if lowered == "load" or lowered.endswith(".load"):
        return "Call when you need to reopen a saved training artifact without retraining."
    if lowered == "forward" or lowered.endswith(".forward"):
        return "PyTorch forward pass used during training and inference; not a shell-facing entrypoint."
    if lowered == "__init__" or lowered.endswith(".__init__"):
        return "Constructor that wires configuration, dimensions, or cached state before the instance is used downstream."
    if lowered.endswith(".to_dict"):
        return "Serialize the current object into a JSON-safe dict for checkpoints or summaries."
    if lowered.endswith(".from_dict"):
        return "Reconstruct the object from saved metadata when reloading a run."
    if lowered.endswith(".use_legacy_path"):
        return "Compatibility helper that tells the caller whether the experiment should fall back to older training logic."
    if lowered.endswith(".positive_rate"):
        return "Convenience property used in logging or monitoring to summarize how many positives are in the current batch."
    if "feature" in lowered and note:
        return f"Use this while working on feature extraction or cache reading inside `{file_rel}`."
    return "Use the surrounding file workflow and the listed callers / outputs to decide where this symbol is invoked in practice."


def heuristic_effects(file_rel: str, symbol_name: str, kind: str) -> str:
    note = FILE_GUIDE_NOTES.get(file_rel, {})
    lowered = symbol_name.lower()
    if lowered == "main":
        return "Produces the file's main side effects or terminal outputs."
    if lowered.startswith("run_"):
        return "Typically triggers most of the file's intended side effects, including artifact writes or model execution."
    if lowered.startswith("analyze_"):
        return "Usually writes plots / tables and returns a structured summary for the phase being analyzed."
    if lowered.startswith("build_") or lowered.startswith("_build_"):
        return "Creates a derived bundle that later stages consume; may also write cache files."
    if lowered.startswith("load_") or lowered.startswith("_load_"):
        return "Reads cached state from disk but should not change model parameters."
    if lowered.startswith("save_") or lowered.startswith("_save_") or lowered.startswith("write_"):
        return "Writes files to disk as its main side effect."
    if lowered == "fit" or lowered.endswith(".fit"):
        return "Updates learned model state and often writes logs or checkpoints after training."
    if lowered == "predict_proba" or lowered.endswith(".predict_proba"):
        return "Returns probabilities only; persistent outputs happen only if the caller saves them."
    if lowered == "forward" or lowered.endswith(".forward"):
        return "Returns tensors for the next layer or final logits; side effects are limited to runtime computation."
    if kind == "class" and note.get("outputs"):
        return "The class itself is a reusable container or module; concrete side effects come from its methods."
    return "Read this together with its caller path to see whether it is pure computation or whether the caller handles persistence."


def module_guide_filename(file_rel: str) -> str:
    stem = file_rel.replace("/", "__").replace(".py", "")
    return f"module-guide__{stem}.md"


def parse_python_inventory(path: Path, project_root: Path) -> list[SymbolDoc]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    file_rel = str(path.relative_to(project_root))
    symbols: list[SymbolDoc] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods: list[SymbolDoc] = []
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_name = f"{node.name}.{child.name}"
                    methods.append(
                        SymbolDoc(
                            kind="method",
                            name=method_name,
                            signature=format_signature(child),
                            start_line=int(child.lineno),
                            end_line=int(getattr(child, "end_lineno", child.lineno)),
                            description=heuristic_description(file_rel, method_name, "method"),
                        )
                    )
            symbols.append(
                SymbolDoc(
                    kind="class",
                    name=node.name,
                    signature=format_signature(node),
                    start_line=int(node.lineno),
                    end_line=int(getattr(node, "end_lineno", node.lineno)),
                    description=heuristic_description(file_rel, node.name, "class"),
                    methods=methods,
                )
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(
                SymbolDoc(
                    kind="function",
                    name=node.name,
                    signature=format_signature(node),
                    start_line=int(node.lineno),
                    end_line=int(getattr(node, "end_lineno", node.lineno)),
                    description=heuristic_description(file_rel, node.name, "function"),
                )
            )
    return symbols


def collect_project_structure(project_root: Path) -> dict[str, Any]:
    top_entries = sorted(
        (
            item
            for item in project_root.iterdir()
            if item.name not in IGNORED_TOP_LEVEL_DIRS
        ),
        key=lambda item: item.name,
    )
    directories = [item.name for item in top_entries if item.is_dir()]
    files = [item.name for item in top_entries if item.is_file()]
    interesting = {}
    for name in ("experiment", "article", "article_code", "other"):
        path = project_root / name
        if path.exists() and path.is_dir():
            interesting[name] = sorted(child.name for child in path.iterdir())[:20]
    return {
        "directories": directories,
        "files": files,
        "interesting_children": interesting,
    }


def collect_dataset_summary(project_root: Path) -> dict[str, Any]:
    sys.path.insert(0, str(project_root))
    import numpy as np

    from experiment.eda.data_loader import load_phase
    from experiment.eda.analysis import compute_temporal_core
    from experiment.training.common import load_experiment_split

    dataset_root = project_root / "experiment" / "dataset"
    dataset_files = sorted(
        str(path.relative_to(project_root))
        for path in dataset_root.rglob("*")
        if path.is_file() and ".ipynb_checkpoints" not in path.parts
    )
    phase1 = load_phase("phase1", repo_root=project_root)
    phase2 = load_phase("phase2", repo_root=project_root)
    split = load_experiment_split(project_root / "experiment" / "outputs" / "eda")
    split_json = safe_json(project_root / "experiment" / "outputs" / "eda" / "recommended_split.json") or {}
    phase1_temporal = compute_temporal_core(phase1)
    phase2_temporal = compute_temporal_core(phase2)

    def phase_payload(phase: Any, split_ids: np.ndarray | None = None) -> dict[str, Any]:
        labels, counts = np.unique(phase.y, return_counts=True)
        label_map = {
            LABEL_NAME_MAP.get(int(label), str(int(label))): int(count)
            for label, count in zip(labels.tolist(), counts.tolist(), strict=True)
        }
        official_train_labels = phase.y[phase.train_mask]
        train_pos = int(np.sum(official_train_labels == 1))
        train_neg = int(np.sum(official_train_labels == 0))
        bg_count = int(label_map.get("background_2", 0) + label_map.get("background_3", 0))
        payload = {
            "num_nodes": int(phase.num_nodes),
            "num_edges": int(phase.num_edges),
            "num_features": int(phase.x.shape[1]),
            "train_size": int(phase.train_mask.size),
            "test_size": int(phase.test_mask.size),
            "label_counts": label_map,
            "official_train_positive_count": train_pos,
            "official_train_negative_count": train_neg,
            "official_train_positive_rate": float(train_pos / max(official_train_labels.size, 1)),
            "official_train_neg_pos_ratio": float(train_neg / max(train_pos, 1)),
            "background_total_count": bg_count,
            "avg_edges_per_node": float(phase.num_edges / max(phase.num_nodes, 1)),
        }
        if split_ids is not None and split_ids.size > 0:
            payload["split_positive_rate"] = float(np.mean(phase.y[split_ids] == 1))
        return payload

    return {
        "dataset_files": dataset_files,
        "phase1": phase_payload(phase1, split.train_ids),
        "phase2": phase_payload(phase2, split.external_ids),
        "phase1_temporal": {
            "first_active_min": int(np.min(phase1_temporal["first_active"])),
            "first_active_median": float(np.median(phase1_temporal["first_active"])),
            "first_active_max": int(np.max(phase1_temporal["first_active"])),
            "active_span_median": float(np.median(phase1_temporal["active_span"])),
        },
        "phase2_temporal": {
            "first_active_min": int(np.min(phase2_temporal["first_active"])),
            "first_active_median": float(np.median(phase2_temporal["first_active"])),
            "first_active_max": int(np.max(phase2_temporal["first_active"])),
            "active_span_median": float(np.median(phase2_temporal["active_span"])),
        },
        "recommended_split": {
            "threshold_day": int(split.threshold_day),
            "train_size": int(split.train_ids.size),
            "val_size": int(split.val_ids.size),
            "external_size": int(split.external_ids.size),
            "train_positive_count": int(np.sum(phase1.y[split.train_ids] == 1)),
            "val_positive_count": int(np.sum(phase1.y[split.val_ids] == 1)),
            "external_positive_count": int(np.sum(phase2.y[split.external_ids] == 1)),
            "train_positive_rate": float(np.mean(phase1.y[split.train_ids] == 1)),
            "val_positive_rate": float(np.mean(phase1.y[split.val_ids] == 1)),
            "external_positive_rate": float(np.mean(phase2.y[split.external_ids] == 1)),
            "train_neg_pos_ratio": float(np.sum(phase1.y[split.train_ids] == 0) / max(np.sum(phase1.y[split.train_ids] == 1), 1)),
            "val_neg_pos_ratio": float(np.sum(phase1.y[split.val_ids] == 0) / max(np.sum(phase1.y[split.val_ids] == 1), 1)),
            "external_neg_pos_ratio": float(np.sum(phase2.y[split.external_ids] == 0) / max(np.sum(phase2.y[split.external_ids] == 1), 1)),
            "train_first_active_median": float(split_json.get("phase1_time_split", {}).get("train_first_active_median", 0.0)),
            "val_first_active_median": float(split_json.get("phase1_time_split", {}).get("val_first_active_median", 0.0)),
        },
    }


def collect_code_inventory(project_root: Path) -> list[dict[str, Any]]:
    files = sorted(
        [
            path
            for path in list((project_root / "experiment" / "eda").glob("*.py"))
            + list((project_root / "experiment" / "training").glob("*.py"))
            if path.name != "__init__.py"
        ]
    )
    inventory = []
    for path in files:
        file_rel = str(path.relative_to(project_root))
        inventory.append(
            {
                "path": file_rel,
                "purpose": FILE_PURPOSES.get(file_rel, "Project module inside experiment/."),
                "symbols": parse_python_inventory(path, project_root),
            }
        )
    return inventory


def extract_metric(summary: dict[str, Any], preferred_keys: list[str], nested_keys: list[tuple[str, str]]) -> float | None:
    for key in preferred_keys:
        value = summary.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    for first, second in nested_keys:
        child = summary.get(first)
        if isinstance(child, dict):
            value = child.get(second)
            if isinstance(value, (int, float)):
                return float(value)
    return None


def collect_results(project_root: Path) -> dict[str, Any]:
    model_root = project_root / "experiment" / "outputs" / "training" / "models"
    rows = []
    for path in sorted(model_root.glob("*/*/summary.json")):
        summary = safe_json(path)
        if not summary:
            continue
        val_auc = extract_metric(
            summary,
            ["phase1_val_auc_mean", "phase1_val_auc"],
            [("phase1_val_metrics", "auc"), ("phase1_val_metrics", "val_auc")],
        )
        external_auc = extract_metric(
            summary,
            ["phase2_external_auc_mean", "phase2_external_auc"],
            [("phase2_external_metrics", "auc")],
        )
        val_ap = extract_metric(summary, [], [("phase1_val_metrics", "ap")])
        if val_ap is None and isinstance(summary.get("phase1_val_ap_mean"), (int, float)):
            val_ap = float(summary["phase1_val_ap_mean"])
        rows.append(
            {
                "path": str(path.relative_to(project_root)),
                "model_name": summary.get("model_name", summary.get("model", path.parent.parent.name)),
                "run_name": summary.get("run_name", path.parent.name),
                "family": path.parent.parent.name,
                "val_auc": val_auc,
                "external_auc": external_auc,
                "val_ap": val_ap,
            }
        )
    rows.sort(
        key=lambda row: (
            row["val_auc"] if row["val_auc"] is not None else -1.0,
            row["external_auc"] if row["external_auc"] is not None else -1.0,
        ),
        reverse=True,
    )
    best = rows[0] if rows else None
    best_by_family: dict[str, dict[str, Any]] = {}
    for row in rows:
        family = str(row["family"])
        if family not in best_by_family:
            best_by_family[family] = row
    return {
        "rows": rows,
        "best": best,
        "best_by_family": best_by_family,
    }


def seed_recent_changes() -> list[dict[str, Any]]:
    return [dict(item) for item in DEFAULT_RECENT_CHANGES]


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def last_commit_entry(project_root: Path) -> dict[str, Any]:
    subject = run_command(["git", "log", "-1", "--pretty=%s"], cwd=project_root)
    files = run_command(["git", "show", "--pretty=", "--name-only", "--diff-filter=ACMRT", "HEAD"], cwd=project_root)
    paths = [line.strip() for line in files.splitlines() if line.strip()]
    return {
        "timestamp": current_timestamp(),
        "title": subject or "Recorded latest git commit",
        "summary": f"Auto-recorded from the latest git commit: {subject}",
        "paths": paths[:12],
    }


def update_recent_changes(skill_root: Path, project_root: Path, args: argparse.Namespace) -> list[dict[str, Any]]:
    refs_dir = ensure_dir(skill_root / "references")
    json_path = refs_dir / "recent-change-memory.json"
    existing = safe_json(json_path)
    if isinstance(existing, dict) and isinstance(existing.get("entries"), list):
        entries = list(existing["entries"])
    elif isinstance(existing, list):
        entries = list(existing)
    else:
        entries = seed_recent_changes()

    new_entry = None
    if args.record_last_commit:
        try:
            new_entry = last_commit_entry(project_root)
        except Exception:
            new_entry = None
    elif args.record_change:
        try:
            status_lines = run_command(["git", "status", "--short"], cwd=project_root).splitlines()
            paths = [line[3:].strip() for line in status_lines if len(line) > 3]
        except Exception:
            paths = []
        new_entry = {
            "timestamp": current_timestamp(),
            "title": args.record_change[:80],
            "summary": args.record_change,
            "paths": paths[:12],
        }

    if new_entry is not None:
        entries.insert(0, new_entry)

    deduped: list[dict[str, Any]] = []
    seen = set()
    for entry in entries:
        key = (entry.get("title"), entry.get("summary"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entry)
    entries = deduped[:5]
    payload = {"entries": entries, "updated_at": current_timestamp()}
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return entries


def render_symbol_detail(file_rel: str, symbol: SymbolDoc) -> list[str]:
    lines = [
        f"### `{symbol.signature}`",
        "",
        f"- Kind: `{symbol.kind}`",
        f"- Lines: `{symbol.start_line}-{symbol.end_line}`",
        f"- Role: {symbol.description}",
        f"- How to use: {heuristic_usage(file_rel, symbol.name, symbol.kind)}",
        f"- Side effects / outputs: {heuristic_effects(file_rel, symbol.name, symbol.kind)}",
    ]
    if symbol.methods:
        lines.append("- Important methods:")
        for method in symbol.methods:
            lines.append(
                f"  - `{method.signature}` lines `{method.start_line}-{method.end_line}`: {method.description}. Usage: {heuristic_usage(file_rel, method.name, 'method')}"
            )
    lines.append("")
    return lines


def render_module_guide(file_info: dict[str, Any]) -> str:
    file_rel = str(file_info["path"])
    note = FILE_GUIDE_NOTES.get(file_rel, {})
    lines = [
        f"# Module Guide: `{file_rel}`",
        "",
        f"## Purpose",
        "",
        file_info["purpose"],
        "",
        "## When To Read This File",
        "",
        note.get("when_to_read", "Read this file when its module role matches the current task."),
        "",
        "## Upstream Callers / Entrypoints",
        "",
    ]
    for item in note.get("upstream", ["No specific upstream note recorded."]):
        lines.append(f"- {item}")
    lines.extend(["", "## Downstream Consumers / Artifacts", ""])
    for item in note.get("downstream", ["No specific downstream note recorded."]):
        lines.append(f"- {item}")
    lines.extend(["", "## Main Outputs Or Side Effects", ""])
    for item in note.get("outputs", ["See the symbol list below."]):
        lines.append(f"- {item}")
    lines.extend(["", "## Common Edit Hotspots", ""])
    for item in note.get("change_points", ["No custom change hotspot note recorded."]):
        lines.append(f"- {item}")
    lines.extend(["", "## Top-Level Symbols", ""])
    if not file_info["symbols"]:
        lines.append("No top-level symbols found.")
        lines.append("")
        return "\n".join(lines) + "\n"
    for symbol in file_info["symbols"]:
        lines.extend(render_symbol_detail(file_rel, symbol))
    return "\n".join(lines) + "\n"


def render_module_guides_index(code_inventory: list[dict[str, Any]]) -> str:
    lines = [
        "# Module Guides Index",
        "",
        "Use this file as the router into the detailed module-level explanations. Each linked guide expands one `experiment/` Python file with purpose, caller path, side effects, and top-level symbol notes.",
        "",
    ]
    for file_info in code_inventory:
        filename = module_guide_filename(str(file_info["path"]))
        lines.append(f"- [{file_info['path']}]({filename}): {file_info['purpose']}")
    return "\n".join(lines) + "\n"


def render_project_handbook(structure: dict[str, Any]) -> str:
    lines = [
        "# Project Handbook",
        "",
        "This file acts as the missing root-level README for the thesis engineering repository.",
        "",
        "## What This Project Is Trying To Do",
        "",
        "The repository is a dynamic-graph anti-fraud graduation project built around the XinYe DGraph benchmark. It combines reproducible EDA, offline feature building, relation-aware GNN training, and fast GPU tabular probes so the team can iterate on leakage-safe experiments rather than ad-hoc notebooks.",
        "",
        "## High-Level Pipeline",
        "",
        "1. Load the raw phase1 / phase2 npz files through `experiment/eda/data_loader.py`.",
        "2. Run EDA through `experiment/eda/analysis.py` and save the recommended time-aware split plus artifact tables.",
        "3. Build offline feature caches and graph caches through `experiment/training/features.py`.",
        "4. Train baseline tabular or GNN models through `experiment/training/run_training.py`.",
        "5. Run faster exploratory GPU XGBoost probes through `experiment/training/run_xgb_*.py`.",
        "6. Compare `summary.json` outputs under `experiment/outputs/training/models/`.",
        "",
        "## Top-Level Folders And Why They Exist",
        "",
    ]
    for name in structure["directories"]:
        note = TOP_LEVEL_NOTES.get(name, "Top-level repository directory with project-specific material.")
        lines.append(f"- `{name}/`: {note}")
    lines.extend(
        [
            "",
            "## Repository Navigation Strategy",
            "",
            "When a new session starts, do not scan the whole repository blindly. Route by task type:",
            "",
            "- If the task is about data meaning, distribution, or split logic, start from `experiment/eda/` and `references/dataset-profile.md`.",
            "- If the task is about model inputs or cached artifacts, start from `experiment/training/features.py` and `experiment/training/README_features.md`.",
            "- If the task is about training behavior, metrics, speed, or GPU usage, start from `experiment/training/run_training.py` and `experiment/training/gnn_models.py`.",
            "- If the task is about comparing completed runs, start from `experiment/outputs/training/models/` and `references/experiment-results-ledger.md`.",
            "- If the task is about future research direction, open `references/optimization-goals.md` and the saved paper notes under `article/`.",
            "",
            "## Recommended Reading Order For A New Session",
            "",
            "1. `references/project-overview.md`",
            "2. `references/dataset-profile.md`",
            "3. `references/experiment-playbook.md`",
            "4. `references/optimization-goals.md`",
            "5. `references/module-guides-index.md`",
            "6. The module guide for the file you are about to change",
            "7. `experiment/training/README_features.md` and `experiment/training/README_gnn_models.md` for the existing long-form manual explanations",
            "",
            "## Typical Task Routing",
            "",
            "- Dataset path or schema issue: start from `experiment/eda/data_loader.py`.",
            "- Split / drift / imbalance question: start from `experiment/eda/analysis.py` and `references/dataset-profile.md`.",
            "- Feature engineering or graph cache question: start from `experiment/training/features.py`.",
            "- User-facing training CLI or summary output question: start from `experiment/training/run_training.py`.",
            "- Backbone, sampling, loss, or GNN speed / accuracy question: start from `experiment/training/gnn_models.py`.",
            "- Fast GPU tabular exploration question: start from `experiment/training/run_xgb_graphprop.py`, `run_xgb_relmean.py`, or `run_xgb_covshift.py`.",
            "",
            "## What Must Stay Stable Across Sessions",
            "",
            "- The project's main evaluation contract is the leakage-safe time-aware split produced by EDA.",
            "- `phase1_val_auc` is the main internal benchmark target and should not be replaced casually by a different metric.",
            "- `summary.json` is the comparison artifact that lets later sessions reason about prior work without rerunning everything.",
            "- The skill itself is meant to be refreshed after code, dataset, feature-cache, or result changes so future sessions inherit the updated state.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_experiment_architecture() -> str:
    lines = [
        "# Experiment Architecture",
        "",
        "## End-To-End Data Flow",
        "",
        "```text",
        "raw phase1/phase2 npz",
        "-> experiment/eda/data_loader.py",
        "-> experiment/eda/analysis.py",
        "-> recommended_split.json + EDA artifacts",
        "-> experiment/training/features.py build_feature_artifacts",
        "-> feature caches + graph caches",
        "-> experiment/training/run_training.py or run_xgb_*.py",
        "-> experiment/outputs/training/models/<family>/<run_name>/summary.json",
        "```",
        "",
        "## Model Families",
        "",
    ]
    for item in MODEL_FAMILY_NOTES:
        lines.append(f"- `{item['name']}` [{item['type']}]: {item['summary']}")
    lines.extend(
        [
            "",
            "## Model Family Detail",
            "",
        ]
    )
    for item in MODEL_FAMILY_NOTES:
        lines.extend(
            [
                f"### `{item['name']}`",
                "",
                f"- Type: `{item['type']}`",
                f"- Core idea: {item['summary']}",
                f"- Typical inputs: {item.get('typical_inputs', 'See the relevant training file.')}",
                f"- Strengths: {item.get('strengths', 'No explicit note recorded.')}",
                f"- Risks: {item.get('risks', 'No explicit note recorded.')}",
                f"- When to use: {item.get('when_to_use', 'Use when it matches the current ablation goal.')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Key Contracts",
            "",
            "- `experiment/outputs/eda/recommended_split.json` defines the main evaluation split contract.",
            "- `FeatureStore` and `GraphCache` are the stable runtime interfaces between offline build and training.",
            "- `summary.json` is the stable comparison artifact for every meaningful experiment run.",
            "",
            "## Artifact Layers",
            "",
            "- Raw dataset layer: `experiment/dataset/phase*_gdata.npz`",
            "- EDA layer: `experiment/outputs/eda/` tables, plots, markdown reports, and `recommended_split.json`",
            "- Cache layer: `experiment/outputs/training/features/` memmaps, manifests, and graph arrays",
            "- Training run layer: `experiment/outputs/training/models/<family>/<run_name>/`",
            "- Skill memory layer: this skill's generated markdown bundle summarizing the live repository state",
            "",
            "## Why This Architecture Exists",
            "",
            "- The dataset is too large for repeated full recomputation during every run.",
            "- Validation is deliberately time-shifted, so experiments need to be reproducible and leakage-safe.",
            "- GNN experiments are slow, so faster GPU tabular probes are needed as a side track for hypothesis testing.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_module_update_hotspots() -> str:
    lines = [
        "# Module Update Hotspots",
        "",
        "Use this file when you already know the type of change you want to make but do not yet know which files to edit.",
        "",
        "## If You Want To Add A New Dataset",
        "",
        "- `experiment/eda/data_loader.py`: add filename resolution and validation logic.",
        "- `experiment/eda/analysis.py`: make sure EDA and split logic still work on the new dataset.",
        "- `references/dataset-profile.md`: the sync script will refresh counts once the loader can see the new data.",
        "",
        "## If You Want To Add Or Change Features",
        "",
        "- `experiment/training/features.py`: add feature construction, manifest spans, and any cache writes.",
        "- `experiment/training/run_training.py`: expose the new feature usage if a model family or CLI flag needs to select it.",
        "- Any probe script under `experiment/training/run_xgb_*.py` that should consume the new feature recipe.",
        "",
        "## If You Want To Change The GNN Backbone",
        "",
        "- `experiment/training/gnn_models.py`: message passing blocks, loss logic, batch construction, logging, and inference live here.",
        "- `experiment/training/run_training.py`: model choices and CLI exposure live here.",
        "- `experiment/training/README_gnn_models.md`: existing hand-written explanation may need updating if you want the manual docs to stay aligned.",
        "",
        "## If You Want To Change Evaluation Or Metrics",
        "",
        "- `experiment/training/common.py`: shared metric definitions.",
        "- `experiment/training/run_training.py`: which metrics are surfaced into summaries.",
        "- `experiment/training/gnn_models.py`: per-epoch logging and curve generation.",
        "",
        "## If You Want Faster Iteration On New Ideas",
        "",
        "- Prefer `run_xgb_graphprop.py`, `run_xgb_relmean.py`, and `run_xgb_covshift.py` before launching a very long GNN run.",
    ]
    return "\n".join(lines) + "\n"


def render_project_overview(structure: dict[str, Any]) -> str:
    lines = [
        "# Project Overview",
        "",
        "## Purpose",
        "",
        "This repository is the working thesis project for dynamic-graph anti-fraud / anomaly detection on the XinYe DGraph benchmark. The main engineering goal is to build reproducible feature, EDA, GNN, and GPU tabular experiment pipelines that can push `phase1_val_auc` to at least `0.82` without leakage.",
        "",
        "## Top-Level Structure",
        "",
    ]
    for name in structure["directories"]:
        lines.append(f"- `{name}/`: {TOP_LEVEL_NOTES.get(name, 'Top-level repository directory with project-specific material.')}")
    if structure["files"]:
        lines.append("")
        lines.append("Top-level files:")
        for name in structure["files"]:
            lines.append(f"- `{name}`")
    lines.extend(
        [
            "",
            "## Directory Snapshots",
            "",
        ]
    )
    for root_name, children in structure["interesting_children"].items():
        lines.append(f"- `{root_name}/`: {', '.join(children)}")
    lines.extend(
        [
            "",
            "## Important Working Areas",
            "",
            "- `experiment/`: main research code. This is the directory to read first for any modeling or evaluation change.",
            "- `experiment/eda/`: reproducible data analysis and split-building logic.",
            "- `experiment/training/`: feature build, LightGBM baseline, GNN stack, and GPU XGBoost exploration scripts.",
            "- `experiment/outputs/`: generated EDA tables, reports, feature caches, model checkpoints, summaries, logs, and predictions.",
            "- `experiment/dataset/`: current XinYe dataset files. The repository currently supports only this dataset family, but the design should evolve toward multi-dataset support.",
            "- `article/` and `article_code/`: paper PDFs, notes, and reference implementations used for research comparison or inspiration rather than direct benchmark truth.",
            "",
            "## Core Engineering Contracts",
            "",
            "- EDA builds the leakage-safe split contract. Training code should consume that split rather than inventing a new one silently.",
            "- Feature caches are reusable assets. Rebuild them only when the raw dataset, feature logic, or cache schema changes.",
            "- Every serious run should produce a persistent directory with `summary.json` so later sessions can compare methods without depending on memory.",
            "- The project is being used for a thesis, so reproducibility and the ability to explain each module matter as much as one-off metric wins.",
            "",
            "## Existing Human-Written Project Docs",
            "",
            "- The repository currently has no root-level README for the thesis project.",
            "- The most important hand-written walkthroughs are:",
            "  - `experiment/training/README_features.md` for the feature-cache and graph-cache pipeline.",
            "  - `experiment/training/README_gnn_models.md` for the GNN implementation and execution flow.",
            "",
            "## Why The Skill Exists",
            "",
            "- New chats should not need to rediscover where the split comes from, what each experiment file does, or which runs were already tried.",
            "- The skill acts as persistent project memory, generated from the live repository rather than handwritten once and left stale.",
            "- Auto-sync keeps the context current after model, feature, dataset, or result changes, with recent-memory capped to the latest five milestones.",
            "",
            "## Current Focus",
            "",
            "- Maintain a stable no-leakage experiment framework.",
            "- Iterate on both GNN and GPU tabular baselines.",
            "- Keep the project context synchronized so new sessions do not need to rediscover the repository, data split, or current AUC ceiling.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_dataset_profile(dataset: dict[str, Any]) -> str:
    split = dataset["recommended_split"]
    phase1 = dataset["phase1"]
    phase2 = dataset["phase2"]
    phase1_temporal = dataset["phase1_temporal"]
    phase2_temporal = dataset["phase2_temporal"]
    lines = [
        "# Dataset Profile",
        "",
        "## Current Dataset Inventory",
        "",
        "The repository currently contains the XinYe DGraph data only. The loading layer still assumes the `phase1` / `phase2` naming convention.",
        "",
    ]
    for path in dataset["dataset_files"]:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Dataset Interpretation",
            "",
            "- `phase1` is the main source for supervised model development and for the time-aware train/validation split used throughout the project.",
            "- `phase2` is treated as the external robustness check after a model is chosen on phase1 validation.",
            "- The skill should be refreshed if these files change, if new dataset files are introduced, or if the loader begins supporting more than the current XinYe layout.",
            "",
            "## Phase Summary",
            "",
            f"- `phase1`: nodes={phase1['num_nodes']}, edges={phase1['num_edges']}, features={phase1['num_features']}, official_train={phase1['train_size']}, official_test={phase1['test_size']}",
            f"- `phase2`: nodes={phase2['num_nodes']}, edges={phase2['num_edges']}, features={phase2['num_features']}, official_train={phase2['train_size']}, official_test={phase2['test_size']}",
            f"- `phase1` official train positive rate: `{phase1['official_train_positive_rate']:.6f}`, neg/pos ratio: `{phase1['official_train_neg_pos_ratio']:.2f}`",
            f"- `phase2` official train positive rate: `{phase2['official_train_positive_rate']:.6f}`, neg/pos ratio: `{phase2['official_train_neg_pos_ratio']:.2f}`",
            f"- Background nodes are numerous: phase1 background total `{phase1['background_total_count']}`, phase2 background total `{phase2['background_total_count']}`",
            f"- Average edges per node: phase1 `{phase1['avg_edges_per_node']:.4f}`, phase2 `{phase2['avg_edges_per_node']:.4f}`",
            "",
            "## Labels",
            "",
            "- `0`: normal",
            "- `1`: fraud",
            "- `2` / `3`: background nodes",
            "- `-100`: test_holdout",
            "",
            "Phase1 label counts:",
        ]
    )
    for name, count in phase1["label_counts"].items():
        lines.append(f"- `{name}`: {count}")
    lines.extend(["", "Phase2 label counts:"])
    for name, count in phase2["label_counts"].items():
        lines.append(f"- `{name}`: {count}")
    lines.extend(
        [
            "",
            "## Temporal Snapshot",
            "",
            f"- phase1 first_active median: `{phase1_temporal['first_active_median']:.2f}` (min `{phase1_temporal['first_active_min']}`, max `{phase1_temporal['first_active_max']}`)",
            f"- phase2 first_active median: `{phase2_temporal['first_active_median']:.2f}` (min `{phase2_temporal['first_active_min']}`, max `{phase2_temporal['first_active_max']}`)",
            f"- phase1 active_span median: `{phase1_temporal['active_span_median']:.2f}`",
            f"- phase2 active_span median: `{phase2_temporal['active_span_median']:.2f}`",
            "",
            "## Recommended Evaluation Split",
            "",
            f"- Time threshold day: `{split['threshold_day']}`",
            f"- phase1 train size: `{split['train_size']}` with `{split['train_positive_count']}` fraud nodes, positive rate `{split['train_positive_rate']:.6f}`",
            f"- phase1 val size: `{split['val_size']}` with `{split['val_positive_count']}` fraud nodes, positive rate `{split['val_positive_rate']:.6f}`",
            f"- phase2 external size: `{split['external_size']}` with `{split['external_positive_count']}` fraud nodes, positive rate `{split['external_positive_rate']:.6f}`",
            f"- phase1 train neg/pos ratio: `{split['train_neg_pos_ratio']:.2f}`",
            f"- phase1 val neg/pos ratio: `{split['val_neg_pos_ratio']:.2f}`",
            f"- phase2 external neg/pos ratio: `{split['external_neg_pos_ratio']:.2f}`",
            f"- phase1 train first_active median: `{split['train_first_active_median']:.2f}`",
            f"- phase1 val first_active median: `{split['val_first_active_median']:.2f}`",
            "",
            "This split is strongly time-shifted: the validation nodes are later than the training nodes. Treat this as the main generalization challenge when AUC stalls around 0.79.",
            "",
            "## What The Split Means Operationally",
            "",
            "- Training code should fit only on `phase1` train ids from `recommended_split.json`.",
            "- Model selection should use `phase1` val ids from the same split.",
            "- External reporting should use `phase2` external ids after model selection, not to tune every idea.",
            "- If a method uses temporal information, later validation or external labels must never leak into earlier supervised training decisions.",
            "",
            "## Why The Imbalance Matters",
            "",
            "- Fraud nodes are rare relative to normal nodes in every supervised split, so AP / PR-AUC are informative diagnostics even when ROC-AUC remains the main target.",
            "- Because the time-aware validation split is later than training, class imbalance interacts with distribution shift rather than standing alone.",
            "",
            "## When To Rebuild Features Or EDA",
            "",
            "- Rerun EDA if the dataset files change, if the split policy changes, or if new temporal statistics are needed.",
            "- Rebuild feature caches if the raw dataset changed, if `features.py` changed, or if the manifest / cache schema changed.",
            "- Do not rebuild caches only because a model hyperparameter changed; model-only experiments should reuse the existing caches when the input definition is unchanged.",
            "",
            "## Dataset Expansion Notes",
            "",
            "- The current `experiment/eda/data_loader.py` resolves only `phase1_gdata.npz` and `phase2_gdata.npz`.",
            "- To add new datasets later, extend the dataset resolver and keep the sync script aware of the new dataset inventory so the skill remains current.",
            "- A future multi-dataset version of this project should expose dataset selection explicitly at the CLI and in the generated skill references.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_code_map(code_inventory: list[dict[str, Any]]) -> str:
    lines = [
        "# Experiment Code Map",
        "",
        "This document is generated from the live repository. It focuses on `experiment/` because that is the benchmark and thesis core.",
        "",
        "Use this file as the fast index. For deeper per-file explanations, jump to `references/module-guides-index.md` and then open the guide for the target module.",
        "",
    ]
    for file_info in code_inventory:
        class_count = sum(1 for symbol in file_info["symbols"] if symbol.kind == "class")
        function_count = sum(1 for symbol in file_info["symbols"] if symbol.kind == "function")
        method_count = sum(len(symbol.methods) for symbol in file_info["symbols"])
        lines.append(f"## `{file_info['path']}`")
        lines.append("")
        lines.append(f"Purpose: {file_info['purpose']}")
        note = FILE_GUIDE_NOTES.get(str(file_info["path"]), {})
        if note.get("when_to_read"):
            lines.append("")
            lines.append(f"When to read: {note['when_to_read']}")
        lines.append("")
        lines.append(f"Inventory summary: {class_count} classes, {function_count} top-level functions, {method_count} documented methods.")
        lines.append("")
        if not file_info["symbols"]:
            lines.append("No top-level symbols found.")
            lines.append("")
            continue
        lines.append("Top-level symbols:")
        for symbol in file_info["symbols"]:
            lines.append(
                f"- `{symbol.signature}` [{symbol.kind}] lines {symbol.start_line}-{symbol.end_line}: {symbol.description}"
            )
            for method in symbol.methods:
                lines.append(
                    f"  - `{method.signature}` [method] lines {method.start_line}-{method.end_line}: {method.description}"
                )
        lines.append("")
    return "\n".join(lines) + "\n"


def render_experiment_playbook(project_root: Path) -> str:
    _ = project_root
    lines = [
        "# Experiment Playbook",
        "",
        "## Environment Rules",
        "",
        "- Activate the `Graph` conda environment before training or feature builds.",
        "- Prefer `python3`, not `python`, because the system default `python` may not point to the intended interpreter.",
        "- Use GPU for heavy training unless the task is explicitly a lightweight CPU smoke test.",
        "- Keep the same CUDA-visible environment and dependency set across comparison runs whenever possible.",
        "",
        "## Core Commands",
        "",
        "Feature build:",
        "",
        "```bash",
        "conda activate Graph",
        "python3 experiment/training/run_training.py build_features --phase both",
        "```",
        "",
        "EDA:",
        "",
        "```bash",
        "conda activate Graph",
        "python3 experiment/eda/run_eda.py --phase both --analysis all",
        "```",
        "",
        "Unified LightGBM / GNN training:",
        "",
        "```bash",
        "conda activate Graph",
        "python3 experiment/training/run_training.py train --model m5_temporal_graphsage --run-name <name> --device cuda",
        "```",
        "",
        "GPU XGBoost probes:",
        "",
        "```bash",
        "conda activate Graph",
        "python3 experiment/training/run_xgb_graphprop.py --run-name <name> --device cuda",
        "python3 experiment/training/run_xgb_relmean.py --run-name <name> --device cuda",
        "python3 experiment/training/run_xgb_covshift.py --run-name <name> --device cuda",
        "```",
        "",
        "## When To Rebuild What",
        "",
        "- Rerun EDA when the raw dataset changes, when the split policy changes, or when temporal/drift analysis needs new artifacts.",
        "- Rebuild feature caches when `features.py` changes, when the feature manifest changes, or when the underlying dataset changed.",
        "- Reuse existing caches when only hyperparameters, losses, samplers, or backbone blocks changed.",
        "- Do not casually mix runs built from different cache generations without writing that difference down in the comparison table.",
        "",
        "## Model Family Intent",
        "",
    ]
    for item in MODEL_FAMILY_NOTES:
        lines.append(f"- `{item['name']}`: {item['summary']}")
    lines.extend(
        [
            "",
            "## Standard Comparison Workflow",
            "",
            "1. Confirm whether the idea is about data/split, features, fast tabular probes, or the online GNN stack.",
            "2. If the idea can be tested with cached tabular features first, run the faster probe before a long GNN experiment.",
            "3. Keep the split contract fixed unless the experiment is explicitly about evaluation design.",
            "4. Record the exact command, run directory, and all changed knobs for every run worth keeping.",
            "5. Compare `phase1_val_auc` first because that is the thesis target.",
            "6. Compare `phase2_external_auc` second to reject brittle improvements.",
            "7. Inspect logs and curves before concluding that a run failed to learn.",
            "",
            "## Suggested Comparison Template",
            "",
            "For every serious run, record:",
            "",
            "- model family and run name",
            "- exact command",
            "- whether EDA or features were rebuilt, and if so from which code state",
            "- feature recipe / negative sampling / loss / sampler choices",
            "- phase1 val AUC",
            "- phase2 external AUC",
            "- PR-AUC / AP if available",
            "- training speed and stability notes",
            "- whether the run is a fair ablation against a specific parent baseline",
            "",
            "## Reading Outputs",
            "",
            "- EDA outputs live under `experiment/outputs/eda/`.",
            "- Feature caches live under `experiment/outputs/training/features/`.",
            "- Model runs live under `experiment/outputs/training/models/<model>/<run_name>/`.",
            "- Each successful run should have a `summary.json`.",
            "- Many GNN runs also include `train.log`, `epoch_metrics.csv`, `metrics.jsonl`, and `training_curves.png`.",
            "",
            "## How To Decide If A Run Is Worth Keeping",
            "",
            "- Keep it if it improves phase1 validation AUC under a fair comparison.",
            "- Keep it if validation is flat but the run reveals a clear speed, stability, or observability gain that future experiments can build on.",
            "- Discard or archive it if it changes too many variables at once and cannot support a clean conclusion.",
            "",
            "## Common Mistakes",
            "",
            "- Comparing runs built from different feature caches without noting that change.",
            "- Optimizing only phase2 external or only AP when the current thesis target is phase1 validation ROC-AUC.",
            "- Forgetting that the main split is time-aware and therefore harder than a random split.",
            "- Launching a long GNN run before a faster probe has tested whether the idea has any signal at all.",
            "- Treating a tiny metric wobble as proof when the run is not matched against a disciplined baseline.",
            "",
            "## No-Leakage Rules",
            "",
            "- Do not train on `phase2` fraud labels when the goal is internal phase1 validation improvement.",
            "- Do not allow later timestamps to influence earlier train batches in time-aware models.",
            "- If using validation distribution information for weighting or adaptation, keep it unsupervised with respect to validation labels.",
            "- If a feature is computed offline, verify that its aggregation window does not peek into future nodes or future labels.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_optimization_goals(results: dict[str, Any]) -> str:
    best = results.get("best")
    best_line = "Current best recorded validation AUC is unavailable."
    if best is not None:
        best_line = (
            f"Current best recorded validation AUC is `{best['val_auc']:.6f}` from "
            f"`{best['path']}`; external AUC is `{best['external_auc']:.6f}`."
        )
    lines = [
        "# Optimization Goals",
        "",
        "## Main Goal",
        "",
    ]
    for note in GOAL_NOTES:
        lines.append(f"- {note}")
    lines.extend(["", best_line, "", "## Open Optimization Directions", ""])
    for item in OPEN_DIRECTIONS:
        lines.append(f"- {item}")
    lines.extend(["", "## Current Best By Family", ""])
    for family, row in sorted(results.get("best_by_family", {}).items()):
        val_auc = "n/a" if row["val_auc"] is None else f"{row['val_auc']:.6f}"
        ext_auc = "n/a" if row["external_auc"] is None else f"{row['external_auc']:.6f}"
        lines.append(f"- `{family}`: val_auc={val_auc}, external_auc={ext_auc}, path=`{row['path']}`")
    lines.extend(
        [
            "",
            "## Success Ladder",
            "",
            "- `<0.79`: still in the current plateau region.",
            "- `0.80+`: meaningful evidence that the new idea is improving phase1 time-split generalization.",
            "- `0.82+`: current user-mandated thesis target.",
            "- `0.82+` with stable external AUC: strong candidate direction worth deeper ablation.",
            "",
            "## What Counts As A Real Improvement",
            "",
            "- The run should be compared against a clear baseline with the same split and broadly the same feature generation state.",
            "- A validation gain that destroys external AUC is not a trustworthy thesis direction.",
            "- A speed or observability gain is useful, but it is not a substitute for the main AUC target unless explicitly framed as infrastructure work.",
            "",
            "## Current Bottleneck Interpretation",
            "",
            "- The project is not obviously failing to fit. Instead, it quickly saturates under a severe time-shifted validation regime.",
            "- Simple extra tabular features and naive graph propagation improved little; relation-specific averaging and covariate-shift weighting were not enough in their current forms.",
            "- This means future work should focus on stronger temporal / relation inductive bias, better sampling, or cleaner graph-tabular hybridization rather than only longer training.",
            "",
            "## Priority Order For Future Work",
            "",
            "- First priority: changes that directly address time-shift generalization without leakage.",
            "- Second priority: faster probes that can cheaply reject weak ideas before long neural runs.",
            "- Third priority: backbone modernization such as stronger attention or Transformer-like blocks, but only if the data/sampling interface is not the real bottleneck.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_results_ledger(results: dict[str, Any]) -> str:
    lines = [
        "# Experiment Results Ledger",
        "",
        "Rows are sorted by validation AUC descending from saved `summary.json` files under `experiment/outputs/training/models/`.",
        "",
        "## Best Run Per Family",
        "",
    ]
    for family, row in sorted(results.get("best_by_family", {}).items()):
        val_auc = "n/a" if row["val_auc"] is None else f"{row['val_auc']:.6f}"
        external_auc = "n/a" if row["external_auc"] is None else f"{row['external_auc']:.6f}"
        lines.append(f"- `{family}`: val_auc={val_auc}, external_auc={external_auc}, path=`{row['path']}`")
    lines.extend(
        [
        "",
        "| Rank | Family | Run | Path | Val AUC | External AUC | Val AP |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ])
    rows = results["rows"][:20]
    for idx, row in enumerate(rows, start=1):
        val_auc = "n/a" if row["val_auc"] is None else f"{row['val_auc']:.6f}"
        external_auc = "n/a" if row["external_auc"] is None else f"{row['external_auc']:.6f}"
        val_ap = "n/a" if row["val_ap"] is None else f"{row['val_ap']:.6f}"
        lines.append(
            f"| {idx} | `{row['family']}` | `{row['run_name']}` | `{row['path']}` | {val_auc} | {external_auc} | {val_ap} |"
        )
    return "\n".join(lines) + "\n"


def render_recent_changes(entries: list[dict[str, Any]]) -> str:
    lines = [
        "# Recent Change Memory",
        "",
        "Only the latest five milestone entries are kept. This file is intended to help new sessions resume the current engineering state quickly.",
        "",
    ]
    for idx, entry in enumerate(entries, start=1):
        lines.append(f"## {idx}. {entry.get('title', 'Untitled change')}")
        lines.append("")
        lines.append(f"- Timestamp: `{entry.get('timestamp', 'unknown')}`")
        lines.append(f"- Summary: {entry.get('summary', '')}")
        paths = entry.get("paths") or []
        if paths:
            lines.append("- Related paths:")
            for path in paths:
                lines.append(f"  - `{path}`")
        lines.append("")
    return "\n".join(lines) + "\n"


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def remove_cache_dirs(path: Path) -> None:
    for cache_dir in path.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)
    for pyc in path.rglob("*.pyc"):
        if pyc.is_file():
            pyc.unlink(missing_ok=True)


def mirror_installed_copy(skill_root: Path) -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    target = codex_home / "skills" / SKILL_NAME
    try:
        if target.exists() and target.resolve() == skill_root.resolve():
            return target
    except Exception:
        pass
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(skill_root, target)
    remove_cache_dirs(target)
    return target


def render_sync_status(project_root: Path, dataset: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
    monitored = build_watch_manifest(project_root)
    return {
        "updated_at": current_timestamp(),
        "project_root": str(project_root),
        "monitored_file_count": len(monitored),
        "dataset_file_count": len(dataset["dataset_files"]),
        "best_result": results.get("best"),
        "fingerprint": hash_manifest(monitored),
    }


def sync_once(project_root: Path, skill_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    references_dir = ensure_dir(skill_root / "references")
    for stale in references_dir.glob("module-guide__*.md"):
        stale.unlink(missing_ok=True)
    structure = collect_project_structure(project_root)
    dataset = collect_dataset_summary(project_root)
    code_inventory = collect_code_inventory(project_root)
    results = collect_results(project_root)
    recent_changes = update_recent_changes(skill_root, project_root, args)

    write_text(references_dir / "project-handbook.md", render_project_handbook(structure))
    write_text(references_dir / "project-overview.md", render_project_overview(structure))
    write_text(references_dir / "dataset-profile.md", render_dataset_profile(dataset))
    write_text(references_dir / "experiment-architecture.md", render_experiment_architecture())
    write_text(references_dir / "experiment-code-map.md", render_code_map(code_inventory))
    write_text(references_dir / "experiment-playbook.md", render_experiment_playbook(project_root))
    write_text(references_dir / "module-update-hotspots.md", render_module_update_hotspots())
    write_text(references_dir / "module-guides-index.md", render_module_guides_index(code_inventory))
    for file_info in code_inventory:
        write_text(
            references_dir / module_guide_filename(str(file_info["path"])),
            render_module_guide(file_info),
        )
    write_text(references_dir / "optimization-goals.md", render_optimization_goals(results))
    write_text(references_dir / "experiment-results-ledger.md", render_results_ledger(results))
    write_text(references_dir / "recent-change-memory.md", render_recent_changes(recent_changes))

    status_payload = render_sync_status(project_root, dataset, results)
    write_text(references_dir / "sync-status.json", json.dumps(status_payload, ensure_ascii=False, indent=2))
    return status_payload


def build_watch_manifest(project_root: Path) -> list[tuple[str, int, int]]:
    patterns = [
        "experiment/eda/*.py",
        "experiment/training/*.py",
        "experiment/outputs/eda/*.json",
        "experiment/outputs/eda/*.md",
        "experiment/outputs/training/models/*/*/summary.json",
        "experiment/dataset/**/*.npz",
        "experiment/dataset/**/*.md",
    ]
    rows: list[tuple[str, int, int]] = []
    for pattern in patterns:
        for path in project_root.glob(pattern):
            if not path.is_file():
                continue
            stat = path.stat()
            rows.append((str(path.relative_to(project_root)), int(stat.st_mtime_ns), int(stat.st_size)))
    rows.sort()
    return rows


def hash_manifest(manifest: list[tuple[str, int, int]]) -> str:
    digest = hashlib.sha1()
    for row in manifest:
        digest.update("|".join(str(part) for part in row).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def install_hooks(project_root: Path, skill_root: Path) -> None:
    script_path = skill_root / "scripts" / "sync_project_context.py"
    hook_body = f"""#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="{project_root}"
SKILL_ROOT="{skill_root}"
SCRIPT_PATH="{script_path}"
if command -v conda >/dev/null 2>&1; then
  conda run -n Graph python3 "$SCRIPT_PATH" --project-root "$PROJECT_ROOT" --skill-root "$SKILL_ROOT" --record-last-commit --mirror-installed-copy >/dev/null 2>&1 || true
else
  python3 "$SCRIPT_PATH" --project-root "$PROJECT_ROOT" --skill-root "$SKILL_ROOT" --record-last-commit --mirror-installed-copy >/dev/null 2>&1 || true
fi
"""
    for hook_name in ("post-commit", "post-merge"):
        hook_path = project_root / ".git" / "hooks" / hook_name
        hook_path.write_text(hook_body, encoding="utf-8")
        os.chmod(hook_path, 0o755)


def watch(project_root: Path, skill_root: Path, args: argparse.Namespace) -> None:
    last_fingerprint = None
    while True:
        manifest = build_watch_manifest(project_root)
        fingerprint = hash_manifest(manifest)
        if fingerprint != last_fingerprint:
            sync_once(project_root, skill_root, args)
            if args.mirror_installed_copy:
                mirror_installed_copy(skill_root)
            last_fingerprint = fingerprint
        time.sleep(max(args.interval, 1.0))


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    skill_root = args.skill_root.resolve()

    if args.install_hook:
        install_hooks(project_root, skill_root)

    if args.watch:
        watch(project_root, skill_root, args)
        return

    status = sync_once(project_root, skill_root, args)
    if args.mirror_installed_copy:
        installed_path = mirror_installed_copy(skill_root)
        status["installed_copy"] = str(installed_path)
    print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
