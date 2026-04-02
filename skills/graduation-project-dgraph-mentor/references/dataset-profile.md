# Dataset Profile

## Current Dataset Inventory

The repository currently contains the XinYe DGraph data only. The loading layer still assumes the `phase1` / `phase2` naming convention.

- `experiment/dataset/XinYe Dataset/B榜数据集/B榜数据集/Readme.md`
- `experiment/dataset/XinYe Dataset/B榜数据集/B榜数据集/phase2_gdata.npz`
- `experiment/dataset/XinYe Dataset/phase1/phase1/Readme.md`
- `experiment/dataset/XinYe Dataset/phase1/phase1/phase1_gdata.npz`

## Dataset Interpretation

- `phase1` is the main source for supervised model development and for the time-aware train/validation split used throughout the project.
- `phase2` is treated as the external robustness check after a model is chosen on phase1 validation.
- The skill should be refreshed if these files change, if new dataset files are introduced, or if the loader begins supporting more than the current XinYe layout.

## Phase Summary

- `phase1`: nodes=4024623, edges=4927620, features=17, official_train=827347, official_test=354578
- `phase2`: nodes=3529572, edges=4363550, features=17, official_train=702387, official_test=301025
- `phase1` official train positive rate: `0.011806`, neg/pos ratio: `83.70`
- `phase2` official train positive rate: `0.011111`, neg/pos ratio: `89.00`
- Background nodes are numerous: phase1 background total `2842698`, phase2 background total `2526160`
- Average edges per node: phase1 `1.2244`, phase2 `1.2363`

## Labels

- `0`: normal
- `1`: fraud
- `2` / `3`: background nodes
- `-100`: test_holdout

Phase1 label counts:
- `test_holdout`: 354578
- `normal`: 817579
- `fraud`: 9768
- `background_2`: 1992982
- `background_3`: 849716

Phase2 label counts:
- `test_holdout`: 301025
- `normal`: 694583
- `fraud`: 7804
- `background_2`: 1854049
- `background_3`: 672111

## Temporal Snapshot

- phase1 first_active median: `139.00` (min `1`, max `578`)
- phase2 first_active median: `249.00` (min `1`, max `690`)
- phase1 active_span median: `0.00`
- phase2 active_span median: `0.00`

## Recommended Evaluation Split

- Time threshold day: `279`
- phase1 train size: `661334` with `7413` fraud nodes, positive rate `0.011209`
- phase1 val size: `166013` with `2355` fraud nodes, positive rate `0.014186`
- phase2 external size: `702387` with `7804` fraud nodes, positive rate `0.011111`
- phase1 train neg/pos ratio: `88.21`
- phase1 val neg/pos ratio: `69.49`
- phase2 external neg/pos ratio: `89.00`
- phase1 train first_active median: `68.00`
- phase1 val first_active median: `418.00`

This split is strongly time-shifted: the validation nodes are later than the training nodes. Treat this as the main generalization challenge when AUC stalls around 0.79.

## What The Split Means Operationally

- Training code should fit only on `phase1` train ids from `recommended_split.json`.
- Model selection should use `phase1` val ids from the same split.
- External reporting should use `phase2` external ids after model selection, not to tune every idea.
- If a method uses temporal information, later validation or external labels must never leak into earlier supervised training decisions.

## Why The Imbalance Matters

- Fraud nodes are rare relative to normal nodes in every supervised split, so AP / PR-AUC are informative diagnostics even when ROC-AUC remains the main target.
- Because the time-aware validation split is later than training, class imbalance interacts with distribution shift rather than standing alone.

## When To Rebuild Features Or EDA

- Rerun EDA if the dataset files change, if the split policy changes, or if new temporal statistics are needed.
- Rebuild feature caches if the raw dataset changed, if `features.py` changed, or if the manifest / cache schema changed.
- Do not rebuild caches only because a model hyperparameter changed; model-only experiments should reuse the existing caches when the input definition is unchanged.

## Dataset Expansion Notes

- The current `experiment/eda/data_loader.py` resolves only `phase1_gdata.npz` and `phase2_gdata.npz`.
- To add new datasets later, extend the dataset resolver and keep the sync script aware of the new dataset inventory so the skill remains current.
- A future multi-dataset version of this project should expose dataset selection explicitly at the CLI and in the generated skill references.
