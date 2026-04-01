# Dataset Profile

## Current Dataset Inventory

The repository currently contains the XinYe DGraph data only. The loading layer still assumes the `phase1` / `phase2` naming convention.

- `experiment/dataset/XinYe Dataset/B榜数据集/B榜数据集/.ipynb_checkpoints/Readme-checkpoint.md`
- `experiment/dataset/XinYe Dataset/B榜数据集/B榜数据集/Readme.md`
- `experiment/dataset/XinYe Dataset/B榜数据集/B榜数据集/phase2_gdata.npz`
- `experiment/dataset/XinYe Dataset/phase1/phase1/Readme.md`
- `experiment/dataset/XinYe Dataset/phase1/phase1/phase1_gdata.npz`

## Phase Summary

- `phase1`: nodes=4024623, edges=4927620, features=17, official_train=827347, official_test=354578
- `phase2`: nodes=3529572, edges=4363550, features=17, official_train=702387, official_test=301025

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

## Recommended Evaluation Split

- Time threshold day: `279`
- phase1 train size: `661334` with `7413` fraud nodes, positive rate `0.011209`
- phase1 val size: `166013` with `2355` fraud nodes, positive rate `0.014186`
- phase2 external size: `702387` with `7804` fraud nodes, positive rate `0.011111`

This split is strongly time-shifted: the validation nodes are later than the training nodes. Treat this as the main generalization challenge when AUC stalls around 0.79.

## Dataset Expansion Notes

- The current `experiment/eda/data_loader.py` resolves only `phase1_gdata.npz` and `phase2_gdata.npz`.
- To add new datasets later, extend the dataset resolver and keep the sync script aware of the new dataset inventory so the skill remains current.
