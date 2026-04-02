# Project Overview

## Purpose

This repository is the working thesis project for dynamic-graph anti-fraud / anomaly detection on the XinYe DGraph benchmark. The main engineering goal is to build reproducible feature, EDA, GNN, and GPU tabular experiment pipelines that can push `phase1_val_auc` to at least `0.82` without leakage.

## Top-Level Structure

- `article/`: Research-paper PDFs, reading notes, Feishu exports, and literature support material. Useful for method inspiration, not as executable benchmark truth.
- `article_code/`: Reference implementations copied from papers or external repos for study, comparison, or selective reuse ideas.
- `experiment/`: The thesis core: EDA, feature building, training entrypoints, model code, and saved outputs.
- `other/`: Miscellaneous utilities or archived material that is not on the main benchmark path.

Top-level files:
- `.codex`
- `.gitattributes`
- `.gitignore`
- `动态图异常检测.zip`

## Directory Snapshots

- `experiment/`: __pycache__, dataset, eda, outputs, training
- `article/`: 2505.15103v2.pdf, Axiomatic.pdf, BOURNE.pdf, GNNPlus.pdf, GNNPlus.zip, GNNPlus_论文深度笔记.feishu-apply-report.json, GNNPlus_论文深度笔记.feishu-audit.json, GNNPlus_论文深度笔记.feishu-audit.md, GNNPlus_论文深度笔记.feishu-live-preview-after.json, GNNPlus_论文深度笔记.feishu-live-preview-before.json, GNNPlus_论文深度笔记.feishu-preview-report.json, GNNPlus_论文深度笔记.format-annotations.json, GNNPlus_论文深度笔记.format-annotations.md, GNNPlus_论文深度笔记.md, GeneralDyG-main.pdf, THGNN.pdf, TransZero.pdf, __pycache__, feishu-backups, feishu_markdown_sync.py
- `article_code/`: Awesome-Deep-Graph-Anomaly-Detection, Axiomatic-Layer-Edges-main, GNNPlus-main, GeneralDyG-main, SAD, SLADE, StrGNN, TADDY_pytorch, TransZero-main, UniGAD, tunedGNN-main
- `other/`: Axiomatic-Layer-Edges, GITA.pdf, GeneralDyG-main, Mymodel, Mymodel.zip, UniGAD.pdf, compare, 【动态图综述】2304.05729v1(1).pdf, 信也科技DGraph金融反欺诈图算法挑战赛 竞赛.html, 信也科技DGraph金融反欺诈图算法挑战赛 竞赛_files, 徐康杰选题相关资料

## Important Working Areas

- `experiment/`: main research code. This is the directory to read first for any modeling or evaluation change.
- `experiment/eda/`: reproducible data analysis and split-building logic.
- `experiment/training/`: feature build, LightGBM baseline, GNN stack, and GPU XGBoost exploration scripts.
- `experiment/outputs/`: generated EDA tables, reports, feature caches, model checkpoints, summaries, logs, and predictions.
- `experiment/dataset/`: current XinYe dataset files. The repository currently supports only this dataset family, but the design should evolve toward multi-dataset support.
- `article/` and `article_code/`: paper PDFs, notes, and reference implementations used for research comparison or inspiration rather than direct benchmark truth.

## Core Engineering Contracts

- EDA builds the leakage-safe split contract. Training code should consume that split rather than inventing a new one silently.
- Feature caches are reusable assets. Rebuild them only when the raw dataset, feature logic, or cache schema changes.
- Every serious run should produce a persistent directory with `summary.json` so later sessions can compare methods without depending on memory.
- The project is being used for a thesis, so reproducibility and the ability to explain each module matter as much as one-off metric wins.

## Existing Human-Written Project Docs

- The repository currently has no root-level README for the thesis project.
- The most important hand-written walkthroughs are:
  - `experiment/training/README_features.md` for the feature-cache and graph-cache pipeline.
  - `experiment/training/README_gnn_models.md` for the GNN implementation and execution flow.

## Why The Skill Exists

- New chats should not need to rediscover where the split comes from, what each experiment file does, or which runs were already tried.
- The skill acts as persistent project memory, generated from the live repository rather than handwritten once and left stale.
- Auto-sync keeps the context current after model, feature, dataset, or result changes, with recent-memory capped to the latest five milestones.

## Current Focus

- Maintain a stable no-leakage experiment framework.
- Iterate on both GNN and GPU tabular baselines.
- Keep the project context synchronized so new sessions do not need to rediscover the repository, data split, or current AUC ceiling.
