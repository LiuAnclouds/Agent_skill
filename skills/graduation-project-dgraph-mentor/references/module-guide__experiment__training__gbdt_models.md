# Module Guide: `experiment/training/gbdt_models.py`

## Purpose

LightGBM baseline wrapper used by the unified training CLI.

## When To Read This File

Read this file when changing the LightGBM baseline behavior inside the unified training CLI.

## Upstream Callers / Entrypoints

- experiment/training/run_training.py::run_train_lightgbm

## Downstream Consumers / Artifacts

- Saved LightGBM boosters and feature importance artifacts

## Main Outputs Or Side Effects

- model.txt
- model_meta.json
- feature_importance.csv

## Common Edit Hotspots

- Tune baseline tabular behavior here if LightGBM remains part of the benchmark contract.

## Top-Level Symbols

### `LightGBMExperiment`

- Kind: `class`
- Lines: `32-145`
- Role: Wrapper around a LightGBM fraud classifier with fit/predict/save/load helpers aligned to this project.
- How to use: Instantiate it inside the training entrypoint, then call `fit(...)`, `predict_proba(...)`, and `save(...)` as needed.
- Side effects / outputs: The class itself is a reusable container or module; concrete side effects come from its methods.
- Important methods:
  - `__init__(self, model_name: str, seed: int, feature_groups: list[str] | None = None, params: dict[str, Any] | None = None) -> None` lines `33-48`: Top-level utility in this module; use the signature and file purpose to understand where it fits in the pipeline.. Usage: Constructor that wires configuration, dimensions, or cached state before the instance is used downstream.
  - `fit(self, train_store: FeatureStore, train_ids: np.ndarray, train_labels: np.ndarray, val_ids: np.ndarray, val_labels: np.ndarray) -> dict[str, float]` lines `50-88`: Train the LightGBM baseline on the phase1 train split and early-stop on phase1 val AUC.. Usage: Call after preparing features, node ids, and labels. This is the optimization stage that updates model parameters.
  - `predict_proba(self, feature_store: FeatureStore, node_ids: np.ndarray) -> np.ndarray` lines `90-95`: Return fraud probabilities for a node-id slice.. Usage: Call on a fitted model to obtain fraud probabilities aligned to the requested node ids.
  - `save(self, run_dir: Path, feature_names: list[str]) -> None` lines `97-112`: Persist the fitted booster and feature-importance metadata.. Usage: Call after a successful fit so later comparison, blending, or deployment steps can reuse the trained artifact.
  - `_write_feature_importance(self, path: Path, feature_names: list[str]) -> None` lines `114-131`: Artifact-writing helper used to persist outputs for later reuse.. Usage: Use this while working on feature extraction or cache reading inside `experiment/training/gbdt_models.py`.
  - `load(cls, run_dir: Path) -> 'LightGBMExperiment'` lines `134-145`: Restore a saved LightGBM experiment from disk.. Usage: Call when you need to reopen a saved training artifact without retraining.

