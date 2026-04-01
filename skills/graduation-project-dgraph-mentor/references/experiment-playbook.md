# Experiment Playbook

## Environment Rules

- Activate the `Graph` conda environment before training or feature builds.
- Prefer `python3`, not `python`, because the system default `python` may not point to the intended interpreter.
- Use GPU for heavy training unless the task is explicitly a lightweight CPU smoke test.

## Core Commands

Feature build:

```bash
conda activate Graph
python3 experiment/training/run_training.py build_features --phase both
```

EDA:

```bash
conda activate Graph
python3 experiment/eda/run_eda.py --phase both --analysis all
```

Unified LightGBM / GNN training:

```bash
conda activate Graph
python3 experiment/training/run_training.py train --model m5_temporal_graphsage --run-name <name> --device cuda
```

GPU XGBoost probes:

```bash
conda activate Graph
python3 experiment/training/run_xgb_graphprop.py --run-name <name> --device cuda
python3 experiment/training/run_xgb_relmean.py --run-name <name> --device cuda
python3 experiment/training/run_xgb_covshift.py --run-name <name> --device cuda
```

## How To Compare Experiments

1. Keep the same recommended split unless the experiment is explicitly about split design.
2. Compare `phase1_val_auc` first because that is the user's main thesis target.
3. Check `phase2_external_auc` next to reject fragile improvements.
4. Use the same feature build and environment when running ablations.
5. Record the run directory and `summary.json` path for every experiment worth keeping.
6. For GNN runs, inspect `train.log`, `epoch_metrics.csv`, and `training_curves.png` before deciding the run has really failed.

## Reading Outputs

- EDA outputs live under `experiment/outputs/eda/`.
- Feature caches live under `experiment/outputs/training/features/`.
- Model runs live under `experiment/outputs/training/models/<model>/<run_name>/`.
- Each successful run should have a `summary.json`; many GNN runs also have per-seed logs and curve plots.

## No-Leakage Rules

- Do not train on `phase2` fraud labels when the goal is internal phase1 validation improvement.
- Do not allow later timestamps to influence earlier train batches in time-aware models.
- If using validation distribution information for weighting or adaptation, keep it unsupervised with respect to validation labels.
