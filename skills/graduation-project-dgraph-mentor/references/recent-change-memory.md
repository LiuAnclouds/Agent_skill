# Recent Change Memory

Only the latest five milestone entries are kept. This file is intended to help new sessions resume the current engineering state quickly.

## 1. Created the graduation-project-dgraph-mentor skill, generated live project refer

- Timestamp: `2026-04-01T19:45:21+08:00`
- Summary: Created the graduation-project-dgraph-mentor skill, generated live project references, installed git hooks, and started a background watcher that mirrors updates back into ~/.codex/skills.
- Related paths:
  - `catboost_info/`
  - `experiment/training/run_xgb_covshift.py`
  - `experiment/training/run_xgb_graphprop.py`
  - `experiment/training/run_xgb_relmean.py`

## 2. Added GPU XGBoost covariate-shift probe

- Timestamp: `2026-04-01T18:17:51+08:00`
- Summary: Introduced run_xgb_covshift.py to test whether weighting phase1 train samples toward the later validation distribution can improve time-split generalization. The first smoke run reached domain_auc=1.0000 but val_auc only about 0.7665.
- Related paths:
  - `experiment/training/run_xgb_covshift.py`
  - `experiment/outputs/training/models/xgboost_gpu/smoke_covshift_m3_v1/summary.json`

## 3. Added GPU XGBoost relation-mean probe

- Timestamp: `2026-04-01T18:15:49+08:00`
- Summary: Introduced run_xgb_relmean.py to test relation-specific neighbor mean features by edge type. The first smoke run underperformed with val_auc about 0.7542, which suggests naive per-relation averaging is too noisy.
- Related paths:
  - `experiment/training/run_xgb_relmean.py`
  - `experiment/outputs/training/models/xgboost_gpu/smoke_relmean_m3_alltypes_rawmiss_v1/summary.json`

## 4. Added GPU XGBoost graph-propagation probe

- Timestamp: `2026-04-01T18:10:24+08:00`
- Summary: Introduced run_xgb_graphprop.py to test propagated feature blocks such as in1/out1/in2/out2 over m2 or m3 features. The full graphprop run reached val_auc about 0.78925, slightly above the plain m3 XGBoost baseline but still far below the 0.82 target.
- Related paths:
  - `experiment/training/run_xgb_graphprop.py`
  - `experiment/outputs/training/models/xgboost_gpu/full_graphprop_m3m2_inout12_v1/summary.json`

## 5. Expanded GNN training observability

- Timestamp: `2026-03-31T20:00:00+08:00`
- Summary: The unified training path now records PR-AUC and AP alongside ROC-AUC, writes per-seed logs and epoch metrics, and saves training curves so long GNN runs are easier to diagnose.
- Related paths:
  - `experiment/training/run_training.py`
  - `experiment/training/gnn_models.py`
  - `experiment/training/common.py`

