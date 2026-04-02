---
name: graduation-project-dgraph-mentor
description: Persistent project-context skill for the Graduation_Project dynamic-graph anti-fraud thesis repository. Use when Codex works on /home/moonxkj/Desktop/MyWork/Graduation_Project and needs the project purpose, repository structure, experiment/ dataset context, code map for experiment/*.py, current AUC target, experiment comparison rules, recent change memory, or must refresh this knowledge after model/data/code updates.
---

# Graduation Project DGraph Mentor

## Overview

Use this skill as the persistent memory and onboarding layer for `/home/moonxkj/Desktop/MyWork/Graduation_Project`.

The skill is not a static note. It ships with a sync script that rebuilds the reference bundle from the live repository, dataset metadata, and experiment outputs.

This skill is intended to answer five recurring problems in new sessions:

1. What the thesis repository is trying to do overall.
2. What each important file under `experiment/` does.
3. What the current dataset, split, and imbalance situation actually are.
4. Which experiments were already tried and what the current AUC target is.
5. Which files should be edited for the next modeling, feature, or evaluation change.

## First Step

When the repository may have changed, run:

```bash
conda run -n Graph python3 scripts/sync_project_context.py \
  --project-root /home/moonxkj/Desktop/MyWork/Graduation_Project \
  --skill-root "$(pwd)"
```

If the task includes a meaningful project update, add a short summary:

```bash
conda run -n Graph python3 scripts/sync_project_context.py \
  --project-root /home/moonxkj/Desktop/MyWork/Graduation_Project \
  --skill-root "$(pwd)" \
  --record-change "Explain the new model or training change here"
```

## Resource Map

- Read [references/project-overview.md](references/project-overview.md) for repository purpose, top-level structure, and where experiments fit.
- Read [references/project-handbook.md](references/project-handbook.md) when you need a synthetic root-level README for the whole thesis repository.
- Read [references/dataset-profile.md](references/dataset-profile.md) for dataset files, labels, split logic, class imbalance, and current expansion notes.
- Read [references/experiment-architecture.md](references/experiment-architecture.md) for the end-to-end pipeline and model-family roles.
- Read [references/experiment-code-map.md](references/experiment-code-map.md) for the `experiment/` code inventory, file roles, top-level functions, classes, and methods.
- Read [references/experiment-playbook.md](references/experiment-playbook.md) for build/train/compare workflow, GPU environment rules, and result interpretation.
- Read [references/module-guides-index.md](references/module-guides-index.md) and then the relevant module guide when you need deeper per-file function explanations.
- Read [references/module-update-hotspots.md](references/module-update-hotspots.md) when you know the type of change you want but not yet which files to edit.
- Read [references/optimization-goals.md](references/optimization-goals.md) for the current target, constraints, bottlenecks, and next optimization directions.
- Read [references/experiment-results-ledger.md](references/experiment-results-ledger.md) for the current leaderboard extracted from saved `summary.json` files.
- Read [references/recent-change-memory.md](references/recent-change-memory.md) for the latest five milestone changes.
- For human-written deep walkthroughs that already exist inside the project, also read:
  - `/home/moonxkj/Desktop/MyWork/Graduation_Project/experiment/training/README_features.md`
  - `/home/moonxkj/Desktop/MyWork/Graduation_Project/experiment/training/README_gnn_models.md`

## Recommended Session Routing

- If the task is "understand the repo first", read:
  - `references/project-overview.md`
  - `references/project-handbook.md`
  - `references/experiment-architecture.md`
- If the task is "understand the data and split", read:
  - `references/dataset-profile.md`
  - `references/optimization-goals.md`
- If the task is "understand a code file before editing", read:
  - `references/module-guides-index.md`
  - the generated module guide for that file
- If the task is "plan or compare experiments", read:
  - `references/experiment-playbook.md`
  - `references/experiment-results-ledger.md`
  - `references/recent-change-memory.md`
- If the task is "choose where to modify the code", read:
  - `references/module-update-hotspots.md`

## Working Rules

1. Treat `phase1_val_auc` as the primary internal target unless the user changes it.
2. Keep `phase2_external_auc` as the main robustness check.
3. Do not introduce leakage across the time-aware split or from `phase2` labels back into `phase1` training.
4. Default to `conda activate Graph` plus `python3`, not `python`.
5. After code, dataset, feature-cache, or experiment-output changes, rerun the sync script before closing the task.
6. Keep the recent-change memory capped at five entries. The sync script enforces that cap.

## What Gets Remembered

- The current repository structure and main experiment pipeline.
- The current dataset inventory, label counts, split statistics, and imbalance notes.
- The current extracted code map and per-module function/class explanations for `experiment/*.py`.
- The latest saved experiment leaderboard from `summary.json` files.
- The latest five milestone changes recorded by hook-triggered syncs or manual `--record-change`.

## Auto Update

The sync script supports two automation modes:

- `--install-hook`
  Installs local `post-commit` and `post-merge` hooks in the project repo so committed changes refresh this skill automatically.
- `--watch`
  Polls the project for changes and refreshes the references on local file updates.

Recommended setup:

```bash
conda run -n Graph python3 scripts/sync_project_context.py \
  --project-root /home/moonxkj/Desktop/MyWork/Graduation_Project \
  --skill-root "$(pwd)" \
  --install-hook
```

If true file-level auto-refresh is needed during active editing, run:

```bash
conda run -n Graph python3 scripts/sync_project_context.py \
  --project-root /home/moonxkj/Desktop/MyWork/Graduation_Project \
  --skill-root "$(pwd)" \
  --watch --interval 20
```

## When To Refresh Which References

- Code changed in `experiment/eda` or `experiment/training`: refresh and read `experiment-code-map.md`.
- A specific file in `experiment/` is about to be edited: refresh and read `module-guides-index.md`, then open that file's generated module guide.
- Dataset files or split logic changed: refresh and read `dataset-profile.md`.
- New training runs finished: refresh and read `experiment-results-ledger.md`.
- The optimization target or benchmark interpretation changed: refresh and read `optimization-goals.md`.

## Completion Rule

Before ending a meaningful project-editing task, make sure the generated references reflect the current repository state. This skill is only useful if it stays synchronized with code, data, and experiment outputs.
