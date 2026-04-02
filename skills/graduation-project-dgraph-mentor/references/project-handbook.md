# Project Handbook

This file acts as the missing root-level README for the thesis engineering repository.

## What This Project Is Trying To Do

The repository is a dynamic-graph anti-fraud graduation project built around the XinYe DGraph benchmark. It combines reproducible EDA, offline feature building, relation-aware GNN training, and fast GPU tabular probes so the team can iterate on leakage-safe experiments rather than ad-hoc notebooks.

## High-Level Pipeline

1. Load the raw phase1 / phase2 npz files through `experiment/eda/data_loader.py`.
2. Run EDA through `experiment/eda/analysis.py` and save the recommended time-aware split plus artifact tables.
3. Build offline feature caches and graph caches through `experiment/training/features.py`.
4. Train baseline tabular or GNN models through `experiment/training/run_training.py`.
5. Run faster exploratory GPU XGBoost probes through `experiment/training/run_xgb_*.py`.
6. Compare `summary.json` outputs under `experiment/outputs/training/models/`.

## Top-Level Folders And Why They Exist

- `article/`: Research-paper PDFs, reading notes, Feishu exports, and literature support material. Useful for method inspiration, not as executable benchmark truth.
- `article_code/`: Reference implementations copied from papers or external repos for study, comparison, or selective reuse ideas.
- `experiment/`: The thesis core: EDA, feature building, training entrypoints, model code, and saved outputs.
- `other/`: Miscellaneous utilities or archived material that is not on the main benchmark path.

## Repository Navigation Strategy

When a new session starts, do not scan the whole repository blindly. Route by task type:

- If the task is about data meaning, distribution, or split logic, start from `experiment/eda/` and `references/dataset-profile.md`.
- If the task is about model inputs or cached artifacts, start from `experiment/training/features.py` and `experiment/training/README_features.md`.
- If the task is about training behavior, metrics, speed, or GPU usage, start from `experiment/training/run_training.py` and `experiment/training/gnn_models.py`.
- If the task is about comparing completed runs, start from `experiment/outputs/training/models/` and `references/experiment-results-ledger.md`.
- If the task is about future research direction, open `references/optimization-goals.md` and the saved paper notes under `article/`.

## Recommended Reading Order For A New Session

1. `references/project-overview.md`
2. `references/dataset-profile.md`
3. `references/experiment-playbook.md`
4. `references/optimization-goals.md`
5. `references/module-guides-index.md`
6. The module guide for the file you are about to change
7. `experiment/training/README_features.md` and `experiment/training/README_gnn_models.md` for the existing long-form manual explanations

## Typical Task Routing

- Dataset path or schema issue: start from `experiment/eda/data_loader.py`.
- Split / drift / imbalance question: start from `experiment/eda/analysis.py` and `references/dataset-profile.md`.
- Feature engineering or graph cache question: start from `experiment/training/features.py`.
- User-facing training CLI or summary output question: start from `experiment/training/run_training.py`.
- Backbone, sampling, loss, or GNN speed / accuracy question: start from `experiment/training/gnn_models.py`.
- Fast GPU tabular exploration question: start from `experiment/training/run_xgb_graphprop.py`, `run_xgb_relmean.py`, or `run_xgb_covshift.py`.

## What Must Stay Stable Across Sessions

- The project's main evaluation contract is the leakage-safe time-aware split produced by EDA.
- `phase1_val_auc` is the main internal benchmark target and should not be replaced casually by a different metric.
- `summary.json` is the comparison artifact that lets later sessions reason about prior work without rerunning everything.
- The skill itself is meant to be refreshed after code, dataset, feature-cache, or result changes so future sessions inherit the updated state.
