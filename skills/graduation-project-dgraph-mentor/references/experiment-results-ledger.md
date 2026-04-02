# Experiment Results Ledger

Rows are sorted by validation AUC descending from saved `summary.json` files under `experiment/outputs/training/models/`.

## Best Run Per Family

- `catboost_gpu`: val_auc=0.784853, external_auc=0.784742, path=`experiment/outputs/training/models/catboost_gpu/probe_m3_catboost_gpu/summary.json`
- `m5_temporal_graphsage`: val_auc=0.786134, external_auc=0.792092, path=`experiment/outputs/training/models/m5_temporal_graphsage/ablate_ratio0/summary.json`
- `m6_temporal_gat`: val_auc=0.782811, external_auc=0.794671, path=`experiment/outputs/training/models/m6_temporal_gat/full_hybrid_v1/summary.json`
- `xgboost_gpu`: val_auc=0.789248, external_auc=0.790223, path=`experiment/outputs/training/models/xgboost_gpu/full_graphprop_m3m2_inout12_v1/summary.json`

| Rank | Family | Run | Path | Val AUC | External AUC | Val AP |
| --- | --- | --- | --- | ---: | ---: | ---: |
| 1 | `xgboost_gpu` | `full_graphprop_m3m2_inout12_v1` | `experiment/outputs/training/models/xgboost_gpu/full_graphprop_m3m2_inout12_v1/summary.json` | 0.789248 | 0.790223 | 0.050511 |
| 2 | `xgboost_gpu` | `probe_m3_xgboost_gpu` | `experiment/outputs/training/models/xgboost_gpu/probe_m3_xgboost_gpu/summary.json` | 0.788915 | 0.790710 | 0.049208 |
| 3 | `xgboost_gpu` | `probe_m3_graphstats_v1` | `experiment/outputs/training/models/xgboost_gpu/probe_m3_graphstats_v1/summary.json` | 0.788629 | 0.787818 | 0.049539 |
| 4 | `xgboost_gpu` | `probe_m3_typetime_v1` | `experiment/outputs/training/models/xgboost_gpu/probe_m3_typetime_v1/summary.json` | 0.786862 | 0.787344 | 0.048921 |
| 5 | `m5_temporal_graphsage` | `ablate_ratio0` | `experiment/outputs/training/models/m5_temporal_graphsage/ablate_ratio0/summary.json` | 0.786134 | 0.792092 | 0.047186 |
| 6 | `xgboost_gpu` | `probe_m3_aug_v1` | `experiment/outputs/training/models/xgboost_gpu/probe_m3_aug_v1/summary.json` | 0.785677 | 0.789190 | 0.048378 |
| 7 | `catboost_gpu` | `probe_m3_catboost_gpu` | `experiment/outputs/training/models/catboost_gpu/probe_m3_catboost_gpu/summary.json` | 0.784853 | 0.784742 | 0.052599 |
| 8 | `m5_temporal_graphsage` | `ablate_ratio5` | `experiment/outputs/training/models/m5_temporal_graphsage/ablate_ratio5/summary.json` | 0.784216 | 0.792938 | 0.047205 |
| 9 | `m6_temporal_gat` | `full_hybrid_v1` | `experiment/outputs/training/models/m6_temporal_gat/full_hybrid_v1/summary.json` | 0.782811 | 0.794671 | 0.046227 |
| 10 | `m5_temporal_graphsage` | `ablate_ratio3` | `experiment/outputs/training/models/m5_temporal_graphsage/ablate_ratio3/summary.json` | 0.782558 | 0.793474 | 0.046642 |
| 11 | `m5_temporal_graphsage` | `cmp_m5_hybrid` | `experiment/outputs/training/models/m5_temporal_graphsage/cmp_m5_hybrid/summary.json` | 0.781776 | 0.794019 | 0.046399 |
| 12 | `m5_temporal_graphsage` | `ablate_ratio1` | `experiment/outputs/training/models/m5_temporal_graphsage/ablate_ratio1/summary.json` | 0.780264 | 0.792395 | 0.045686 |
| 13 | `m5_temporal_graphsage` | `m5_hardneg_focalrank_v1` | `experiment/outputs/training/models/m5_temporal_graphsage/m5_hardneg_focalrank_v1/summary.json` | 0.779158 | 0.790592 | 0.045676 |
| 14 | `xgboost_gpu` | `smoke_covshift_m3_v1` | `experiment/outputs/training/models/xgboost_gpu/smoke_covshift_m3_v1/summary.json` | 0.766460 | 0.784634 | 0.048838 |
| 15 | `xgboost_gpu` | `smoke_graphprop_m3m2_v1` | `experiment/outputs/training/models/xgboost_gpu/smoke_graphprop_m3m2_v1/summary.json` | 0.759751 | 0.803741 | 0.048445 |
| 16 | `xgboost_gpu` | `smoke_relmean_m3_alltypes_rawmiss_v1` | `experiment/outputs/training/models/xgboost_gpu/smoke_relmean_m3_alltypes_rawmiss_v1/summary.json` | 0.754235 | 0.788256 | 0.051708 |
| 17 | `xgboost_gpu` | `probe_m3_with_background_v1` | `experiment/outputs/training/models/xgboost_gpu/probe_m3_with_background_v1/summary.json` | 0.725008 | 0.635772 | 0.029992 |
| 18 | `m5_temporal_graphsage` | `smoke_hardneg_loss` | `experiment/outputs/training/models/m5_temporal_graphsage/smoke_hardneg_loss/summary.json` | 0.683468 | 0.646904 | 0.063187 |
| 19 | `m6_temporal_gat` | `smoke_m6_hybrid` | `experiment/outputs/training/models/m6_temporal_gat/smoke_m6_hybrid/summary.json` | 0.664062 | 0.544137 | 0.171891 |
