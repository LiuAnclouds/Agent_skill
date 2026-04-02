# Optimization Goals

## Main Goal

- Primary internal target: push phase1_val_auc to at least 0.82 without any data leakage.
- Keep phase2_external_auc as the robustness check; improving val while collapsing external generalization is not acceptable.
- Use GPU in the Graph conda environment for heavy experiments. The user explicitly requested GPU rather than CPU training.
- Current evidence suggests the hard temporal split is the main bottleneck: phase1 train nodes are much earlier than phase1 val nodes, so distribution shift is severe.

Current best recorded validation AUC is `0.789248` from `experiment/outputs/training/models/xgboost_gpu/full_graphprop_m3m2_inout12_v1/summary.json`; external AUC is `0.790223`.

## Open Optimization Directions

- Improve time-aware sampling or time-conditioned feature engineering without leaking future information.
- Strengthen relation-aware modeling instead of global averaging. The current simple relation-mean probe was too weak, but more selective relation features remain open.
- Keep exploring GPU tabular models and graph-tabular hybrids because they are faster to iterate than long GNN runs.
- Revisit backbone updates such as stronger temporal GAT / Transformer-style modules once a faster feature or sampling baseline is stable.
- Consider calibrated ensembling or stacking only after a clearly stronger single-run validation model appears.
- Prepare the data-loading layer for future additional datasets; the current repository still assumes only the XinYe DGraph phase1/phase2 layout.

## Current Best By Family

- `catboost_gpu`: val_auc=0.784853, external_auc=0.784742, path=`experiment/outputs/training/models/catboost_gpu/probe_m3_catboost_gpu/summary.json`
- `m5_temporal_graphsage`: val_auc=0.786134, external_auc=0.792092, path=`experiment/outputs/training/models/m5_temporal_graphsage/ablate_ratio0/summary.json`
- `m6_temporal_gat`: val_auc=0.782811, external_auc=0.794671, path=`experiment/outputs/training/models/m6_temporal_gat/full_hybrid_v1/summary.json`
- `xgboost_gpu`: val_auc=0.789248, external_auc=0.790223, path=`experiment/outputs/training/models/xgboost_gpu/full_graphprop_m3m2_inout12_v1/summary.json`

## Success Ladder

- `<0.79`: still in the current plateau region.
- `0.80+`: meaningful evidence that the new idea is improving phase1 time-split generalization.
- `0.82+`: current user-mandated thesis target.
- `0.82+` with stable external AUC: strong candidate direction worth deeper ablation.

## What Counts As A Real Improvement

- The run should be compared against a clear baseline with the same split and broadly the same feature generation state.
- A validation gain that destroys external AUC is not a trustworthy thesis direction.
- A speed or observability gain is useful, but it is not a substitute for the main AUC target unless explicitly framed as infrastructure work.

## Current Bottleneck Interpretation

- The project is not obviously failing to fit. Instead, it quickly saturates under a severe time-shifted validation regime.
- Simple extra tabular features and naive graph propagation improved little; relation-specific averaging and covariate-shift weighting were not enough in their current forms.
- This means future work should focus on stronger temporal / relation inductive bias, better sampling, or cleaner graph-tabular hybridization rather than only longer training.

## Priority Order For Future Work

- First priority: changes that directly address time-shift generalization without leakage.
- Second priority: faster probes that can cheaply reject weak ideas before long neural runs.
- Third priority: backbone modernization such as stronger attention or Transformer-like blocks, but only if the data/sampling interface is not the real bottleneck.
