# Experiment Playbook

## Environment Rules

- Activate the `Graph` conda environment before training or feature builds.
- Prefer `python3`, not `python`, because the system default `python` may not point to the intended interpreter.
- Use GPU for heavy training unless the task is explicitly a lightweight CPU smoke test.
- Keep the same CUDA-visible environment and dependency set across comparison runs whenever possible.

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

## When To Rebuild What

- Rerun EDA when the raw dataset changes, when the split policy changes, or when temporal/drift analysis needs new artifacts.
- Rebuild feature caches when `features.py` changes, when the feature manifest changes, or when the underlying dataset changed.
- Reuse existing caches when only hyperparameters, losses, samplers, or backbone blocks changed.
- Do not casually mix runs built from different cache generations without writing that difference down in the comparison table.

## Model Family Intent

- `m1_tabular`: Raw node features plus missingness baseline.
- `m2_hybrid`: Handcrafted structural, background, edge-type, and time features built in features.py.
- `m3_neighbor`: m2_hybrid plus offline 1-hop neighbor aggregation blocks.
- `m4_graphsage`: Relation-aware GraphSAGE baseline without explicit temporal encoding.
- `m5_temporal_graphsage`: Time-aware relation GraphSAGE benchmark with modern training options.
- `m6_temporal_gat`: Temporal relation attention backbone that replaces SAGE aggregation with attention-style message passing.
- `xgboost_gpu probes`: Fast CUDA XGBoost exploration track for graph-propagation, relation-mean, and covariate-shift ideas.

## Standard Comparison Workflow

1. Confirm whether the idea is about data/split, features, fast tabular probes, or the online GNN stack.
2. If the idea can be tested with cached tabular features first, run the faster probe before a long GNN experiment.
3. Keep the split contract fixed unless the experiment is explicitly about evaluation design.
4. Record the exact command, run directory, and all changed knobs for every run worth keeping.
5. Compare `phase1_val_auc` first because that is the thesis target.
6. Compare `phase2_external_auc` second to reject brittle improvements.
7. Inspect logs and curves before concluding that a run failed to learn.

## Suggested Comparison Template

For every serious run, record:

- model family and run name
- exact command
- whether EDA or features were rebuilt, and if so from which code state
- feature recipe / negative sampling / loss / sampler choices
- phase1 val AUC
- phase2 external AUC
- PR-AUC / AP if available
- training speed and stability notes
- whether the run is a fair ablation against a specific parent baseline

## Reading Outputs

- EDA outputs live under `experiment/outputs/eda/`.
- Feature caches live under `experiment/outputs/training/features/`.
- Model runs live under `experiment/outputs/training/models/<model>/<run_name>/`.
- Each successful run should have a `summary.json`.
- Many GNN runs also include `train.log`, `epoch_metrics.csv`, `metrics.jsonl`, and `training_curves.png`.

## How To Decide If A Run Is Worth Keeping

- Keep it if it improves phase1 validation AUC under a fair comparison.
- Keep it if validation is flat but the run reveals a clear speed, stability, or observability gain that future experiments can build on.
- Discard or archive it if it changes too many variables at once and cannot support a clean conclusion.

## Common Mistakes

- Comparing runs built from different feature caches without noting that change.
- Optimizing only phase2 external or only AP when the current thesis target is phase1 validation ROC-AUC.
- Forgetting that the main split is time-aware and therefore harder than a random split.
- Launching a long GNN run before a faster probe has tested whether the idea has any signal at all.
- Treating a tiny metric wobble as proof when the run is not matched against a disciplined baseline.

## No-Leakage Rules

- Do not train on `phase2` fraud labels when the goal is internal phase1 validation improvement.
- Do not allow later timestamps to influence earlier train batches in time-aware models.
- If using validation distribution information for weighting or adaptation, keep it unsupervised with respect to validation labels.
- If a feature is computed offline, verify that its aggregation window does not peek into future nodes or future labels.
