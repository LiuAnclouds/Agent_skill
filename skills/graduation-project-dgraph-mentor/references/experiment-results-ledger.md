# Experiment Results Ledger

Rows are sorted by validation AUC descending from saved `summary.json` files under `experiment/outputs/training/models/`.

## Best Run Per Family

- `catboost_gpu`: val_auc=0.784853, external_auc=0.784742, path=`experiment/outputs/training/models/catboost_gpu/probe_m3_catboost_gpu/summary.json`
- `m5_temporal_graphsage`: val_auc=0.787012, external_auc=0.798524, path=`experiment/outputs/training/models/m5_temporal_graphsage/m5_temporal_tb30_seed42_8ep_v2/summary.json`
- `m6_temporal_gat`: val_auc=0.782811, external_auc=0.794671, path=`experiment/outputs/training/models/m6_temporal_gat/full_hybrid_v1/summary.json`
- `xgboost_gpu`: val_auc=0.795341, external_auc=0.791805, path=`experiment/outputs/training/models/xgboost_gpu/multiclass_bg_graphprop_decay20_bw025_v1/summary.json`

| Rank | Family | Run | Path | Val AUC | External AUC | Val AP |
| --- | --- | --- | --- | ---: | ---: | ---: |
| 1 | `xgboost_gpu` | `multiclass_bg_graphprop_decay20_bw025_v1` | `experiment/outputs/training/models/xgboost_gpu/multiclass_bg_graphprop_decay20_bw025_v1/summary.json` | 0.795341 | 0.791805 | 0.052565 |
| 2 | `xgboost_gpu` | `multiclass_bg_graphprop_decay90_bw025_v1` | `experiment/outputs/training/models/xgboost_gpu/multiclass_bg_graphprop_decay90_bw025_v1/summary.json` | 0.794696 | 0.794171 | 0.052819 |
| 3 | `xgboost_gpu` | `multiclass_bg_graphprop_decay20_bw010_v1` | `experiment/outputs/training/models/xgboost_gpu/multiclass_bg_graphprop_decay20_bw010_v1/summary.json` | 0.794680 | 0.791443 | 0.052173 |
| 4 | `xgboost_gpu` | `multiclass_bg_graphprop_decay20_90_bw025_v1` | `experiment/outputs/training/models/xgboost_gpu/multiclass_bg_graphprop_decay20_90_bw025_v1/summary.json` | 0.794661 | 0.786716 | 0.053215 |
| 5 | `xgboost_gpu` | `multiclass_bg_graphprop_decay20_v1` | `experiment/outputs/training/models/xgboost_gpu/multiclass_bg_graphprop_decay20_v1/summary.json` | 0.794632 | 0.791464 | 0.053329 |
| 6 | `xgboost_gpu` | `multiclass_bg_graphprop_decay20_bw025_baseTB30_v1` | `experiment/outputs/training/models/xgboost_gpu/multiclass_bg_graphprop_decay20_bw025_baseTB30_v1/summary.json` | 0.794605 | 0.791149 | 0.051841 |
| 7 | `xgboost_gpu` | `multiclass_bg_graphprop_m2base_decay20_bw025_v1` | `experiment/outputs/training/models/xgboost_gpu/multiclass_bg_graphprop_m2base_decay20_bw025_v1/summary.json` | 0.794237 | 0.790459 | 0.052729 |
| 8 | `xgboost_gpu` | `multiclass_bg_graphprop_decay20_bw025_fw125_v1` | `experiment/outputs/training/models/xgboost_gpu/multiclass_bg_graphprop_decay20_bw025_fw125_v1/summary.json` | 0.794229 | 0.791302 | 0.052067 |
| 9 | `xgboost_gpu` | `multiclass_bg_graphprop_decay20_bw025_tb30_v1` | `experiment/outputs/training/models/xgboost_gpu/multiclass_bg_graphprop_decay20_bw025_tb30_v1/summary.json` | 0.794040 | 0.791974 | 0.053233 |
| 10 | `xgboost_gpu` | `pseudo_decay20_p085_n001_w015_v1` | `experiment/outputs/training/models/xgboost_gpu/pseudo_decay20_p085_n001_w015_v1/summary.json` | 0.793789 | 0.791752 | 0.050240 |
| 11 | `xgboost_gpu` | `pseudo_decay90_p085_n001_w015_v1` | `experiment/outputs/training/models/xgboost_gpu/pseudo_decay90_p085_n001_w015_v1/summary.json` | 0.793526 | 0.791849 | 0.051541 |
| 12 | `xgboost_gpu` | `full_temporal_safe_graphprop_decay20_v1` | `experiment/outputs/training/models/xgboost_gpu/full_temporal_safe_graphprop_decay20_v1/summary.json` | 0.793202 | 0.791488 | 0.051165 |
| 13 | `xgboost_gpu` | `full_temporal_safe_graphprop_decay90_v1` | `experiment/outputs/training/models/xgboost_gpu/full_temporal_safe_graphprop_decay90_v1/summary.json` | 0.792824 | 0.792171 | 0.052458 |
| 14 | `xgboost_gpu` | `multiclass_bg_m3_temporal_tb30_bw050_v1` | `experiment/outputs/training/models/xgboost_gpu/multiclass_bg_m3_temporal_tb30_bw050_v1/summary.json` | 0.792732 | 0.796278 | 0.051499 |
| 15 | `xgboost_gpu` | `full_temporal_safe_graphprop_decay20_90_v1` | `experiment/outputs/training/models/xgboost_gpu/full_temporal_safe_graphprop_decay20_90_v1/summary.json` | 0.792236 | 0.787475 | 0.049951 |
| 16 | `xgboost_gpu` | `full_temporal_safe_graphprop_out1_decay20_v1` | `experiment/outputs/training/models/xgboost_gpu/full_temporal_safe_graphprop_out1_decay20_v1/summary.json` | 0.792095 | 0.789184 | 0.049851 |
| 17 | `xgboost_gpu` | `pseudo_temporal_safe_p085_n001_w015_v1` | `experiment/outputs/training/models/xgboost_gpu/pseudo_temporal_safe_p085_n001_w015_v1/summary.json` | 0.791769 | 0.792123 | 0.050710 |
| 18 | `xgboost_gpu` | `full_temporal_safe_graphprop_decay20_inout12_v1` | `experiment/outputs/training/models/xgboost_gpu/full_temporal_safe_graphprop_decay20_inout12_v1/summary.json` | 0.791735 | 0.790240 | 0.050436 |
| 19 | `xgboost_gpu` | `full_temporal_safe_graphstats_sim_graphprop_decay20_v1` | `experiment/outputs/training/models/xgboost_gpu/full_temporal_safe_graphstats_sim_graphprop_decay20_v1/summary.json` | 0.791561 | 0.787379 | 0.050229 |
| 20 | `xgboost_gpu` | `full_temporal_safe_graphprop_decay15_v1` | `experiment/outputs/training/models/xgboost_gpu/full_temporal_safe_graphprop_decay15_v1/summary.json` | 0.791510 | 0.788393 | 0.049000 |
