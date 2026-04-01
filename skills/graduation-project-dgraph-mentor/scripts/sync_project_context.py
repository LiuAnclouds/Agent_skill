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
    top_entries = sorted(project_root.iterdir(), key=lambda item: item.name)
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
    from experiment.training.common import load_experiment_split

    dataset_root = project_root / "experiment" / "dataset"
    dataset_files = sorted(
        str(path.relative_to(project_root))
        for path in dataset_root.rglob("*")
        if path.is_file()
    )
    phase1 = load_phase("phase1", repo_root=project_root)
    phase2 = load_phase("phase2", repo_root=project_root)
    split = load_experiment_split(project_root / "experiment" / "outputs" / "eda")

    def phase_payload(phase: Any, split_ids: np.ndarray | None = None) -> dict[str, Any]:
        labels, counts = np.unique(phase.y, return_counts=True)
        payload = {
            "num_nodes": int(phase.num_nodes),
            "num_edges": int(phase.num_edges),
            "num_features": int(phase.x.shape[1]),
            "train_size": int(phase.train_mask.size),
            "test_size": int(phase.test_mask.size),
            "label_counts": {
                LABEL_NAME_MAP.get(int(label), str(int(label))): int(count)
                for label, count in zip(labels.tolist(), counts.tolist(), strict=True)
            },
        }
        if split_ids is not None and split_ids.size > 0:
            payload["split_positive_rate"] = float(np.mean(phase.y[split_ids] == 1))
        return payload

    return {
        "dataset_files": dataset_files,
        "phase1": phase_payload(phase1, split.train_ids),
        "phase2": phase_payload(phase2, split.external_ids),
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
        },
    }


def collect_code_inventory(project_root: Path) -> list[dict[str, Any]]:
    files = sorted(
        list((project_root / "experiment" / "eda").glob("*.py"))
        + list((project_root / "experiment" / "training").glob("*.py"))
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
    return {
        "rows": rows,
        "best": best,
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
        lines.append(f"- `{name}/`")
    if structure["files"]:
        lines.append("")
        lines.append("Top-level files:")
        for name in structure["files"]:
            lines.append(f"- `{name}`")
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
            "## Existing Human-Written Project Docs",
            "",
            "- The repository currently has no root-level README for the thesis project.",
            "- The most important hand-written walkthroughs are:",
            "  - `experiment/training/README_features.md` for the feature-cache and graph-cache pipeline.",
            "  - `experiment/training/README_gnn_models.md` for the GNN implementation and execution flow.",
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
            "## Phase Summary",
            "",
            f"- `phase1`: nodes={phase1['num_nodes']}, edges={phase1['num_edges']}, features={phase1['num_features']}, official_train={phase1['train_size']}, official_test={phase1['test_size']}",
            f"- `phase2`: nodes={phase2['num_nodes']}, edges={phase2['num_edges']}, features={phase2['num_features']}, official_train={phase2['train_size']}, official_test={phase2['test_size']}",
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
            "## Recommended Evaluation Split",
            "",
            f"- Time threshold day: `{split['threshold_day']}`",
            f"- phase1 train size: `{split['train_size']}` with `{split['train_positive_count']}` fraud nodes, positive rate `{split['train_positive_rate']:.6f}`",
            f"- phase1 val size: `{split['val_size']}` with `{split['val_positive_count']}` fraud nodes, positive rate `{split['val_positive_rate']:.6f}`",
            f"- phase2 external size: `{split['external_size']}` with `{split['external_positive_count']}` fraud nodes, positive rate `{split['external_positive_rate']:.6f}`",
            "",
            "This split is strongly time-shifted: the validation nodes are later than the training nodes. Treat this as the main generalization challenge when AUC stalls around 0.79.",
            "",
            "## Dataset Expansion Notes",
            "",
            "- The current `experiment/eda/data_loader.py` resolves only `phase1_gdata.npz` and `phase2_gdata.npz`.",
            "- To add new datasets later, extend the dataset resolver and keep the sync script aware of the new dataset inventory so the skill remains current.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_code_map(code_inventory: list[dict[str, Any]]) -> str:
    lines = [
        "# Experiment Code Map",
        "",
        "This document is generated from the live repository. It focuses on `experiment/` because that is the benchmark and thesis core.",
        "",
    ]
    for file_info in code_inventory:
        lines.append(f"## `{file_info['path']}`")
        lines.append("")
        lines.append(f"Purpose: {file_info['purpose']}")
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
    lines = [
        "# Experiment Playbook",
        "",
        "## Environment Rules",
        "",
        "- Activate the `Graph` conda environment before training or feature builds.",
        "- Prefer `python3`, not `python`, because the system default `python` may not point to the intended interpreter.",
        "- Use GPU for heavy training unless the task is explicitly a lightweight CPU smoke test.",
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
        "## How To Compare Experiments",
        "",
        "1. Keep the same recommended split unless the experiment is explicitly about split design.",
        "2. Compare `phase1_val_auc` first because that is the user's main thesis target.",
        "3. Check `phase2_external_auc` next to reject fragile improvements.",
        "4. Use the same feature build and environment when running ablations.",
        "5. Record the run directory and `summary.json` path for every experiment worth keeping.",
        "6. For GNN runs, inspect `train.log`, `epoch_metrics.csv`, and `training_curves.png` before deciding the run has really failed.",
        "",
        "## Reading Outputs",
        "",
        "- EDA outputs live under `experiment/outputs/eda/`.",
        "- Feature caches live under `experiment/outputs/training/features/`.",
        "- Model runs live under `experiment/outputs/training/models/<model>/<run_name>/`.",
        "- Each successful run should have a `summary.json`; many GNN runs also have per-seed logs and curve plots.",
        "",
        "## No-Leakage Rules",
        "",
        "- Do not train on `phase2` fraud labels when the goal is internal phase1 validation improvement.",
        "- Do not allow later timestamps to influence earlier train batches in time-aware models.",
        "- If using validation distribution information for weighting or adaptation, keep it unsupervised with respect to validation labels.",
    ]
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
    lines.extend(
        [
            "",
            "## Current Bottleneck Interpretation",
            "",
            "- The project is not obviously failing to fit. Instead, it quickly saturates under a severe time-shifted validation regime.",
            "- Simple extra tabular features and naive graph propagation improved little; relation-specific averaging and covariate-shift weighting were not enough in their current forms.",
            "- This means future work should focus on stronger temporal / relation inductive bias, better sampling, or cleaner graph-tabular hybridization rather than only longer training.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_results_ledger(results: dict[str, Any]) -> str:
    lines = [
        "# Experiment Results Ledger",
        "",
        "Rows are sorted by validation AUC descending from saved `summary.json` files under `experiment/outputs/training/models/`.",
        "",
        "| Rank | Path | Val AUC | External AUC | Val AP |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    rows = results["rows"][:20]
    for idx, row in enumerate(rows, start=1):
        val_auc = "n/a" if row["val_auc"] is None else f"{row['val_auc']:.6f}"
        external_auc = "n/a" if row["external_auc"] is None else f"{row['external_auc']:.6f}"
        val_ap = "n/a" if row["val_ap"] is None else f"{row['val_ap']:.6f}"
        lines.append(f"| {idx} | `{row['path']}` | {val_auc} | {external_auc} | {val_ap} |")
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
    structure = collect_project_structure(project_root)
    dataset = collect_dataset_summary(project_root)
    code_inventory = collect_code_inventory(project_root)
    results = collect_results(project_root)
    recent_changes = update_recent_changes(skill_root, project_root, args)

    write_text(references_dir / "project-overview.md", render_project_overview(structure))
    write_text(references_dir / "dataset-profile.md", render_dataset_profile(dataset))
    write_text(references_dir / "experiment-code-map.md", render_code_map(code_inventory))
    write_text(references_dir / "experiment-playbook.md", render_experiment_playbook(project_root))
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
