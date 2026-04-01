# Project Overview

## Purpose

This repository is the working thesis project for dynamic-graph anti-fraud / anomaly detection on the XinYe DGraph benchmark. The main engineering goal is to build reproducible feature, EDA, GNN, and GPU tabular experiment pipelines that can push `phase1_val_auc` to at least `0.82` without leakage.

## Top-Level Structure

- `.claude/`
- `.git/`
- `.idea/`
- `article/`
- `article_code/`
- `catboost_info/`
- `experiment/`
- `other/`

Top-level files:
- `.codex`
- `.gitattributes`
- `.gitignore`
- `动态图异常检测.zip`

## Important Working Areas

- `experiment/`: main research code. This is the directory to read first for any modeling or evaluation change.
- `experiment/eda/`: reproducible data analysis and split-building logic.
- `experiment/training/`: feature build, LightGBM baseline, GNN stack, and GPU XGBoost exploration scripts.
- `experiment/outputs/`: generated EDA tables, reports, feature caches, model checkpoints, summaries, logs, and predictions.
- `experiment/dataset/`: current XinYe dataset files. The repository currently supports only this dataset family, but the design should evolve toward multi-dataset support.
- `article/` and `article_code/`: paper PDFs, notes, and reference implementations used for research comparison or inspiration rather than direct benchmark truth.

## Existing Human-Written Project Docs

- The repository currently has no root-level README for the thesis project.
- The most important hand-written walkthroughs are:
  - `experiment/training/README_features.md` for the feature-cache and graph-cache pipeline.
  - `experiment/training/README_gnn_models.md` for the GNN implementation and execution flow.

## Current Focus

- Maintain a stable no-leakage experiment framework.
- Iterate on both GNN and GPU tabular baselines.
- Keep the project context synchronized so new sessions do not need to rediscover the repository, data split, or current AUC ceiling.
